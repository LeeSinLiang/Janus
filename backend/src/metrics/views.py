from django.shortcuts import render
import os, requests, time, threading
from dotenv import load_dotenv
from django.conf import settings
from .models import PostMetrics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from twitter_clone.models import CloneComment
from .serializer import PostMetricsSerializer, PostSerializer, ContentVariantSerializer
from agents.models import Post, ContentVariant, Campaign
from requests_oauthlib import OAuth1
from time import time
from django.core.cache import cache
from agents import create_trigger_parser
from django.db import connection, transaction
from django.db.utils import OperationalError



# Create your views here.
def getMetricsDB():
	posts = Post.objects.filter(status="published").select_related('metrics')
	out = {}
	for post in posts:
		m = getattr(post, "metrics", None)
		if m:
			# Use max metrics (winner of A and B) for canvas display
			max_metrics = m.get_max_metrics()
			out[int(post.pk)] = {
				"likes": max_metrics['likes'],
				"comments": max_metrics['comments'],
				"retweets": max_metrics['retweets'],
			}
		else:
			out[int(post.pk)] = {
				"likes": 0,
				"comments": 0,
				"retweets": 0,
			}
	return out

@api_view(['POST'])
def setTrigger(request):
	pk = request.data.get("pk")
	trigger = request.data.get("trigger")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)
	if not trigger:
		return Response({"error": "Missing 'trigger' field"}, status=400)

	try:
		post = Post.objects.get(pk=pk)
	except Post.DoesNotExist:
		return Response({"error": f"Post {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

	# This endpoint is deprecated - use parseTrigger instead
	# Kept for backward compatibility
	return Response({"error": "This endpoint is deprecated. Use /api/parse-trigger/ instead."}, status=400)

@api_view(['POST'])
def parseTrigger(request):
	"""Parse natural language trigger prompt and save to post"""
	pk = request.data.get("pk")
	condition = request.data.get("condition")
	prompt = request.data.get("prompt")

	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)
	if not condition:
		return Response({"error": "Missing 'condition' field"}, status=400)
	if not prompt:
		return Response({"error": "Missing 'prompt' field"}, status=400)

	# Validate condition is in allowed choices
	valid_conditions = ['likes', 'retweets', 'impressions', 'comments']
	if condition not in valid_conditions:
		return Response({
			"error": f"Invalid condition '{condition}'. Must be one of: {', '.join(valid_conditions)}"
		}, status=400)

	try:
		post = Post.objects.get(pk=pk)
	except Post.DoesNotExist:
		return Response({"error": f"Post {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

	try:
		# Create trigger parser agent and parse the prompt
		parser = create_trigger_parser()
		trigger_config = parser.parse(condition, prompt)

		# Save parsed trigger to post
		post.trigger_condition = condition
		post.trigger_value = trigger_config.value
		post.trigger_comparison = trigger_config.comparison
		post.trigger_prompt = trigger_config.prompt
		post.save()

		return Response({
			"success": True,
			"post_id": post.pk,
			"trigger": {
				"condition": condition,
				"value": trigger_config.value,
				"comparison": trigger_config.comparison,
				"prompt": trigger_config.prompt
			}
		}, status=status.HTTP_200_OK)

	except Exception as e:
		return Response({
			"error": f"Failed to parse trigger: {str(e)}"
		}, status=500)

###### FOR AI AGENT TO DETERMINE NEW DIRECTION/STRATEGY ######
def getMetricsAI(pk):
	post = Post.objects.get(pk=pk)
	metrics = post.metrics
	output = {
		'title': post.title,
		'description': post.description,
		'likes': metrics.likes,
		'retweets': metrics.retweets,
		'commentList': metrics.commentList
	}
	return output

def retry_on_db_lock(func, max_retries=5, initial_delay=0.1):
	"""
	Retry a database operation with exponential backoff if it fails due to database lock.
	"""
	delay = initial_delay
	last_exception = None

	for attempt in range(max_retries):
		try:
			return func()
		except OperationalError as e:
			if "database is locked" in str(e).lower():
				last_exception = e
				if attempt < max_retries - 1:
					time.sleep(delay)
					delay *= 2
			else:
				raise
	raise last_exception


def regenerate_content_background(triggered_post_data):
	"""
	Background task to regenerate content for a triggered post.

	This function:
	1. Analyzes metrics with trigger context
	2. Regenerates improved A/B content variants
	3. Generates media assets for new variants
	4. Updates post status to draft for user review
	5. Clears trigger configuration

	Args:
		triggered_post_data: Dict with post_pk, trigger details, metrics, etc.
	"""
	# IMPORTANT: Close any existing database connections
	connection.close()

	try:
		from agents.metrics_analyzer import create_metrics_analyzer
		from agents.content_creator import create_content_creator, save_content_variants_for_post
		from agents.media_creator import create_media_creator
		import base64
		from django.core.files.base import ContentFile

		# Get the post object with retry
		def get_post():
			return Post.objects.get(pk=triggered_post_data["post_pk"])

		post = retry_on_db_lock(get_post)

		# Build metrics data for analysis
		metrics_data = {
			"variant_a": {
				"condition": triggered_post_data["trigger_condition"],
				"value": triggered_post_data["current_value_a"],
				"content": post.variants.filter(variant_id='A').order_by('-created_at').first().content if post.variants.filter(variant_id='A').exists() else ""
			},
			"variant_b": {
				"condition": triggered_post_data["trigger_condition"],
				"value": triggered_post_data["current_value_b"],
				"content": post.variants.filter(variant_id='B').order_by('-created_at').first().content if post.variants.filter(variant_id='B').exists() else ""
			},
			"elapsed_time_seconds": triggered_post_data["elapsed_time_seconds"]
		}

		# Step 1: Initialize agents (outside transaction)
		print(f"[Trigger] Analyzing metrics for post {post.pk} ({post.title})...")
		metrics_agent = create_metrics_analyzer()
		content_agent = create_content_creator()
		media_agent = create_media_creator(model_name='models/gemini-2.5-flash-image')

		# Step 2: Execute metrics analyzer for trigger-specific analysis
		analysis_report = metrics_agent.execute_trigger_analysis(
			metrics_data=metrics_data,
			condition=triggered_post_data["trigger_condition"],
			trigger_value=triggered_post_data["trigger_value"],
			comparison=triggered_post_data["trigger_comparison"],
			trigger_prompt=triggered_post_data["trigger_prompt"],
			triggered_variants=triggered_post_data["triggered_variants"]
		)

		print(f"[Trigger] Generating improved content for post {post.pk}...")

		# Step 3: Get existing variants and campaign info
		def get_post_data():
			p = Post.objects.select_related('campaign').prefetch_related('variants').get(pk=post.pk)
			return p, p.campaign

		post, campaign = retry_on_db_lock(get_post_data)

		existing_variants = post.variants.all().order_by('created_at')
		old_content_parts = []
		for variant in existing_variants:
			old_content_parts.append(f"Variant {variant.variant_id}: {variant.content}")
		old_content = "\n".join(old_content_parts)

		product_info = campaign.metadata.get('product_info', '') if campaign.metadata else ''

		# Step 4: Generate improved content using execute_with_metrics
		content_output = content_agent.execute_with_metrics(
			title=post.title,
			description=post.description,
			product_info=product_info,
			old_content=old_content,
			analyzed_report=analysis_report.analysis
		)

		print(f"[Trigger] Saving new variants with media for post {post.pk}...")

		# Step 5: Create NEW ContentVariant records with media (keep old ones for history)
		def create_variant_a():
			with transaction.atomic():
				return ContentVariant.objects.create(
					post=post,
					variant_id='A',
					content=content_output.A,
					platform='X',
					metadata={'image_caption': content_output.A_image_caption, 'regenerated': True}
				)

		variant_a = retry_on_db_lock(create_variant_a)

		# Generate and save media for Variant A
		try:
			asset_a = media_agent.create_image(prompt=content_output.A_image_caption)
			mime_type = asset_a['mime_type']
			ext = mime_type.split('/')[-1]
			data = ContentFile(base64.b64decode(asset_a['data']))

			def save_variant_a_asset():
				variant_a.asset.save(f'variant_a_image_{post.post_id}_{int(time.time())}.{ext}', data, save=True)

			retry_on_db_lock(save_variant_a_asset)
			print(f"[Trigger] Generated media for variant A")
		except Exception as e:
			print(f"[Trigger] Warning: Failed to generate image for variant A: {e}")

		# Create Variant B
		def create_variant_b():
			with transaction.atomic():
				return ContentVariant.objects.create(
					post=post,
					variant_id='B',
					content=content_output.B,
					platform='X',
					metadata={'image_caption': content_output.B_image_caption, 'regenerated': True}
				)

		variant_b = retry_on_db_lock(create_variant_b)

		# Generate and save media for Variant B
		try:
			asset_b = media_agent.create_image(prompt=content_output.B_image_caption)
			mime_type = asset_b['mime_type']
			ext = mime_type.split('/')[-1]
			data = ContentFile(base64.b64decode(asset_b['data']))

			def save_variant_b_asset():
				variant_b.asset.save(f'variant_b_image_{post.post_id}_{int(time.time())}.{ext}', data, save=True)

			retry_on_db_lock(save_variant_b_asset)
			print(f"[Trigger] Generated media for variant B")
		except Exception as e:
			print(f"[Trigger] Warning: Failed to generate image for variant B: {e}")

		# Step 6: Update post status and clear trigger
		def update_post_status():
			with transaction.atomic():
				p = Post.objects.get(pk=post.pk)
				p.status = 'draft'
				p.trigger_condition = None
				p.trigger_value = None
				p.trigger_comparison = None
				p.trigger_prompt = None
				p.save()

		retry_on_db_lock(update_post_status)

		print(f"✅ [Trigger] Successfully regenerated content for post {post.pk} ({post.title})")
		print(f"   New Variant A: {content_output.A[:50]}...")
		print(f"   New Variant B: {content_output.B[:50]}...")

	except Exception as e:
		print(f"❌ [Trigger] Error regenerating content for post {triggered_post_data.get('post_pk', 'unknown')}: {e}")
		import traceback
		traceback.print_exc()

	finally:
		# Close database connection when thread is done
		connection.close()


@api_view(['GET'])
def checkTrigger(request):
	"""Check if any published posts meet their trigger conditions"""
	from django.utils import timezone

	# Get campaign_id from query params (optional)
	campaign_id = request.GET.get('campaign_id')

	# Filter published posts that have triggers configured
	query = Post.objects.filter(
		status="published",
		trigger_condition__isnull=False,
		trigger_value__isnull=False,
		trigger_comparison__isnull=False
	)

	# Filter by campaign if campaign_id provided
	if campaign_id:
		query = query.filter(campaign__campaign_id=campaign_id)

	publishedPosts = query.select_related('metrics').order_by('created_at')

	triggeredPosts = []

	for post in publishedPosts:
		# Skip if post hasn't been posted yet or metrics don't exist
		if not post.posted_time or not post.metrics:
			continue

		# Calculate elapsed time since posting
		elapsed_time = (timezone.now() - post.posted_time).total_seconds()

		# Get metrics for both A/B variants
		metrics_a = post.metrics.get_variant_metrics('A')
		metrics_b = post.metrics.get_variant_metrics('B')

		# Get the specific metric value for both variants based on trigger_condition
		metric_value_a = metrics_a.get(post.trigger_condition, 0)
		metric_value_b = metrics_b.get(post.trigger_condition, 0)

		# Evaluate the comparison for both variants
		is_triggered_a = False
		is_triggered_b = False

		if post.trigger_comparison == '<':
			is_triggered_a = metric_value_a < post.trigger_value
			is_triggered_b = metric_value_b < post.trigger_value
		elif post.trigger_comparison == '=':
			is_triggered_a = metric_value_a == post.trigger_value
			is_triggered_b = metric_value_b == post.trigger_value
		elif post.trigger_comparison == '>':
			is_triggered_a = metric_value_a > post.trigger_value
			is_triggered_b = metric_value_b > post.trigger_value

		# Trigger if either variant meets the condition
		is_triggered = is_triggered_a or is_triggered_b

		if is_triggered:
			# Track which variant(s) triggered
			triggered_variants = []
			if is_triggered_a:
				triggered_variants.append('A')
			if is_triggered_b:
				triggered_variants.append('B')

			triggeredPosts.append({
				"post_pk": post.pk,
				"post_title": post.title,
				"trigger_condition": post.trigger_condition,
				"trigger_value": post.trigger_value,
				"trigger_comparison": post.trigger_comparison,
				"current_value_a": metric_value_a,
				"current_value_b": metric_value_b,
				"triggered_variants": triggered_variants,
				"elapsed_time_seconds": elapsed_time,
				"trigger_prompt": post.trigger_prompt
			})

	if triggeredPosts:
		print(f"Triggered {len(triggeredPosts)} post(s):", triggeredPosts)

		# Launch background threads to regenerate content for each triggered post
		for triggered_post_data in triggeredPosts:
			try:
				# Launch background task (returns immediately)
				regeneration_thread = threading.Thread(
					target=regenerate_content_background,
					args=(triggered_post_data,),
					daemon=True
				)
				regeneration_thread.start()
				print(f"[Trigger] Launched regeneration thread for post {triggered_post_data['post_pk']}")

			except Exception as e:
				print(f"❌ Error launching regeneration thread for post {triggered_post_data['post_pk']}: {e}")
				# Continue processing other posts even if one fails
				continue

	return Response({
		"triggered_posts": triggeredPosts,
		"count": len(triggeredPosts),
		"message": f"Triggers fired for {len(triggeredPosts)} post(s). Content regeneration started in background." if triggeredPosts else "No triggers fired."
	}, status=200)

@api_view(['GET'])
def nodesJSON(request):
	# Get campaign_id from query params, fallback to first campaign
	campaign_id = request.GET.get('campaign_id')

	if campaign_id:
		try:
			campaign = Campaign.objects.get(campaign_id=campaign_id)
		except Campaign.DoesNotExist:
			return Response({
				"error": f"Campaign with id '{campaign_id}' not found"
			}, status=404)
	else:
		campaign = Campaign.objects.first()

	if not campaign:
		return Response({
			"error": "No campaigns found"
		}, status=404)

	posts = Post.objects.filter(campaign=campaign)
	serializer = PostSerializer(posts, many=True)
	metricsData = getMetricsDB()

	# Include campaign status information
	campaign_info = {
		"campaign_id": campaign.campaign_id,
		"name": campaign.name,
		"phase": campaign.phase,
		"description": campaign.description,
	}

	# Get first 4 published posts with metrics for the chart view
	published_posts = Post.objects.filter(status="published").select_related('metrics').order_by('created_at')
	chartPosts = published_posts[:4]

	post_metrics = []
	for post in chartPosts:
		m = getattr(post, "metrics", None)
		if m:
			# Use aggregated metrics (sum of A and B) for chart view
			aggregated = m.get_aggregated_metrics()
			post_metrics.append({
				"pk": post.pk,
				"title": post.title,
				"description": post.description,
				"likes": aggregated['likes'],
				"retweets": aggregated['retweets'],
				"impressions": aggregated['impressions'],
				"comments": aggregated['comments'],
			})
		else:
			post_metrics.append({
				"pk": post.pk,
				"title": post.title,
				"description": post.description,
				"likes": 0,
				"retweets": 0,
				"impressions": 0,
				"comments": 0,
			})

	return Response({
		"diagram": serializer.data,
		"metrics": metricsData,
		"campaign": campaign_info,
		"post_metrics": post_metrics
	}, status=200)

@api_view(['POST'])
def createXPost(request):
	pk = request.data.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)

	post = Post.objects.get(pk=pk)

	# Get both variants A and B (latest versions only)
	variant_a = ContentVariant.objects.filter(variant_id="A", post=post).order_by('-created_at').first()
	variant_b = ContentVariant.objects.filter(variant_id="B", post=post).order_by('-created_at').first()

	results = {}
	errors = []

	# Post variant A
	if variant_a:
		text_a = variant_a.content
		media_a = getattr(getattr(variant_a, "asset", None), "name", None)

		try:
			resp_a = requests.post(
				"http://localhost:8000/clone/2/tweets",
				headers={"Content-Type": "application/json"},
				json={"text": text_a, "media": media_a}
			)
			if resp_a.status_code == 201:
				tweet_id_a = resp_a.json().get("data", {}).get("id")
				results['A'] = tweet_id_a
			else:
				errors.append(f"Variant A failed: {resp_a.text}")
		except Exception as e:
			errors.append(f"Variant A error: {str(e)}")

	# Post variant B
	if variant_b:
		text_b = variant_b.content
		media_b = getattr(getattr(variant_b, "asset", None), "name", None)

		try:
			resp_b = requests.post(
				"http://localhost:8000/clone/2/tweets",
				headers={"Content-Type": "application/json"},
				json={"text": text_b, "media": media_b}
			)
			if resp_b.status_code == 201:
				tweet_id_b = resp_b.json().get("data", {}).get("id")
				results['B'] = tweet_id_b
			else:
				errors.append(f"Variant B failed: {resp_b.text}")
		except Exception as e:
			errors.append(f"Variant B error: {str(e)}")

	# Update PostMetrics with both tweet_ids (A/B structure)
	postMetrics = post.metrics
	if postMetrics:
		# Preserve existing structure, update tweet_ids
		current_tweet_ids = postMetrics.tweet_id if isinstance(postMetrics.tweet_id, dict) else {}
		current_tweet_ids.update(results)
		postMetrics.tweet_id = current_tweet_ids
		postMetrics.save()

	# Mark post as published if at least one variant was posted
	if results:
		post.status = "published"
		# Set posted_time for trigger evaluation
		from django.utils import timezone
		post.posted_time = timezone.now()
		post.save()

	response_data = {
		"success": bool(results),
		"tweet_ids": results,
	}

	if errors:
		response_data["errors"] = errors

	return Response(response_data, status=201 if results else 400)

@api_view(['POST'])
def getXPostMetrics(request):
	pk = request.data.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)

	post = Post.objects.get(pk=pk)
	postMetrics = post.metrics
	tweet_ids = postMetrics.tweet_id  # Now a dict: {"A": "123", "B": "456"}

	# Initialize metrics storage
	metrics_results = {
		"likes": {},
		"retweets": {},
		"impressions": {},
		"comments": {},
		"commentList": {}
	}

	# Use clone API instead of real Twitter API
	url = f"http://localhost:8000/clone/2/metrics/"
	headers = {"Content-Type": "application/json"}

	# Fetch metrics for both variants
	for variant in ['A', 'B']:
		tweet_id = tweet_ids.get(variant) if isinstance(tweet_ids, dict) else None

		# Skip if no tweet_id for this variant (backward compatibility)
		if not tweet_id:
			metrics_results["likes"][variant] = 0
			metrics_results["retweets"][variant] = 0
			metrics_results["impressions"][variant] = 0
			metrics_results["comments"][variant] = 0
			metrics_results["commentList"][variant] = []
			continue

		# Fetch metrics for this variant
		body = {"tweet_ids": tweet_id}
		resp = requests.post(url, headers=headers, json=body)

		if resp.status_code != 200:
			# If API call fails, set metrics to 0
			metrics_results["likes"][variant] = 0
			metrics_results["retweets"][variant] = 0
			metrics_results["impressions"][variant] = 0
			metrics_results["comments"][variant] = 0
			metrics_results["commentList"][variant] = []
			continue

		data = resp.json()
		items = data.get("data") or []

		if not items:
			# Tweet not found, set to 0
			metrics_results["likes"][variant] = 0
			metrics_results["retweets"][variant] = 0
			metrics_results["impressions"][variant] = 0
			metrics_results["comments"][variant] = 0
			metrics_results["commentList"][variant] = []
			continue

		# Extract metrics from response
		d = items[0]
		pub = d.get("public_metrics", {})
		nonpub = d.get("non_public_metrics", {})

		metrics_results["retweets"][variant] = pub.get("retweet_count", 0)
		metrics_results["likes"][variant] = pub.get("like_count", 0)
		metrics_results["comments"][variant] = pub.get("reply_count", 0)
		metrics_results["impressions"][variant] = nonpub.get("impression_count", 0)

		# Get comment list
		commentList = CloneComment.objects.filter(
			tweet__tweet_id=tweet_id
		).order_by('-created_at').values_list('text', flat=True)
		metrics_results["commentList"][variant] = list(commentList)

	# Update PostMetrics with A/B structure
	postMetrics.likes = metrics_results["likes"]
	postMetrics.retweets = metrics_results["retweets"]
	postMetrics.impressions = metrics_results["impressions"]
	postMetrics.comments = metrics_results["comments"]
	postMetrics.commentList = metrics_results["commentList"]
	postMetrics.save()

	# Return aggregated response
	return Response({
		"status": "success",
		"metrics": {
			"A": postMetrics.get_variant_metrics('A'),
			"B": postMetrics.get_variant_metrics('B')
		}
	}, status=200)

@api_view(['GET'])
def metricsJSON(request):
	qs = PostMetrics.objects.all()
	serializer = PostMetricsSerializer(qs, many=True)
	return Response(serializer.data)

@api_view(['GET'])
def getVariants(request):
	"""Get content variants for a post by pk"""
	pk = request.GET.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' parameter"}, status=400)

	try:
		post = Post.objects.get(pk=pk)
		variants = post.variants.all()  # Uses related_name='variants' from ContentVariant model
		serializer = ContentVariantSerializer(variants, many=True)
		return Response({"variants": serializer.data}, status=200)
	except Post.DoesNotExist:
		return Response({"error": f"Post with pk={pk} not found"}, status=404)

@api_view(['POST'])
def selectVariant(request):
	"""Save selected variant for a post and update post description"""
	pk = request.data.get("pk")
	variant_id = request.data.get("variant_id")

	if not pk or not variant_id:
		return Response({"error": "Missing 'pk' or 'variant_id' field"}, status=400)

	try:
		post = Post.objects.get(pk=pk)
		# Verify the variant exists (get latest version)
		variant = post.variants.filter(variant_id=variant_id).order_by('-created_at').first()

		if not variant:
			return Response({"error": f"Variant '{variant_id}' not found for post {pk}"}, status=404)

		# Save selected variant and update post description with variant content
		post.selected_variant = variant_id
		post.description = variant.content
		post.save()

		return Response({
			"success": True,
			"message": f"Variant '{variant_id}' selected for post {pk}",
			"post_id": post.pk,
			"selected_variant": variant_id,
			"updated_description": variant.content
		}, status=200)
	except Post.DoesNotExist:
		return Response({"error": f"Post with pk={pk} not found"}, status=404)

@api_view(['POST'])
def approveNode(request):
	"""Approve a pending node"""
	pk = request.data.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)

	# Find the post by pk
	try:
		post = Post.objects.get(pk=pk)
		# Mark as approved (you can add an 'approved' field to the model later)
		# For now, just return success
		return Response({
			"success": True,
			"message": f"Node '{post.title}' (pk={post.pk}) approved",
			"post_id": post.pk
		}, status=200)
	except Post.DoesNotExist:
		return Response({
			"error": f"Post with pk={pk} not found"
		}, status=404)

@api_view(['POST'])
def rejectNode(request):
	"""Reject a pending node and remove it"""
	pk = request.data.get("pk")
	reject_message = request.data.get("reject_message", "")

	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)

	# Find the post by pk
	try:
		post = Post.objects.get(pk=pk)
		post_id = post.pk
		post_title = post.title
		# Delete the post
		post.delete()

		return Response({
			"success": True,
			"message": f"Node '{post_title}' (pk={post_id}) rejected and removed",
			"reject_message": reject_message,
			"post_id": post_id
		}, status=200)
	except Post.DoesNotExist:
		return Response({
			"error": f"Post with pk={pk} not found"
		}, status=404)

@api_view(['POST'])
def approveAllNodes(request):
	"""Approve all draft posts in a campaign and publish them to X"""
	campaign_id = request.data.get("campaign_id")

	if not campaign_id:
		return Response({"error": "Missing 'campaign_id' field"}, status=400)

	try:
		# Get the campaign
		campaign = Campaign.objects.get(campaign_id=campaign_id)

		# Find all draft posts for this campaign
		draft_posts = Post.objects.filter(campaign=campaign, status='draft')

		if not draft_posts.exists():
			return Response({
				"success": True,
				"message": "No draft posts found to approve",
				"approved_count": 0,
				"campaign_id": campaign_id
			}, status=200)

		approved_count = 0
		failed_posts = []

		# Approve each draft post and create X post for BOTH variants
		for post in draft_posts:
			try:
				# Get both variants A and B (latest versions only)
				variant_a = ContentVariant.objects.filter(variant_id="A", post=post).order_by('-created_at').first()
				variant_b = ContentVariant.objects.filter(variant_id="B", post=post).order_by('-created_at').first()

				results = {}
				post_errors = []

				# Post variant A
				if variant_a:
					text_a = variant_a.content
					media_a = getattr(getattr(variant_a, "asset", None), "name", None)

					try:
						resp_a = requests.post(
							"http://localhost:8000/clone/2/tweets",
							headers={"Content-Type": "application/json"},
							json={"text": text_a, "media": media_a}
						)
						if resp_a.status_code == 201:
							tweet_id_a = resp_a.json().get("data", {}).get("id")
							results['A'] = tweet_id_a
						else:
							post_errors.append(f"Variant A failed: {resp_a.text}")
					except Exception as e:
						post_errors.append(f"Variant A error: {str(e)}")

				# Post variant B
				if variant_b:
					text_b = variant_b.content
					media_b = getattr(getattr(variant_b, "asset", None), "name", None)

					try:
						resp_b = requests.post(
							"http://localhost:8000/clone/2/tweets",
							headers={"Content-Type": "application/json"},
							json={"text": text_b, "media": media_b}
						)
						if resp_b.status_code == 201:
							tweet_id_b = resp_b.json().get("data", {}).get("id")
							results['B'] = tweet_id_b
						else:
							post_errors.append(f"Variant B failed: {resp_b.text}")
					except Exception as e:
						post_errors.append(f"Variant B error: {str(e)}")

				# If at least one variant posted successfully
				if results:
					# Update post metrics with both tweet_ids
					post_metrics = post.metrics
					if post_metrics:
						post_metrics.tweet_id = results  # {"A": "123", "B": "456"}
						post_metrics.save()

					# Update post status to published and set posted_time
					from django.utils import timezone
					post.status = 'published'
					post.posted_time = timezone.now()
					post.save()
					approved_count += 1

					# Record any partial failures
					if post_errors:
						failed_posts.append({
							"post_id": post.pk,
							"title": post.title,
							"error": f"Partial success: {', '.join(post_errors)}"
						})
				else:
					failed_posts.append({
						"post_id": post.pk,
						"title": post.title,
						"error": f"Both variants failed: {', '.join(post_errors) if post_errors else 'No variants found'}"
					})

			except Exception as e:
				failed_posts.append({"post_id": post.pk, "title": post.title, "error": str(e)})

		response_data = {
			"success": True,
			"message": f"Approved and published {approved_count} draft post(s)",
			"approved_count": approved_count,
			"campaign_id": campaign_id
		}

		if failed_posts:
			response_data["failed_posts"] = failed_posts
			response_data["message"] += f" ({len(failed_posts)} failed)"

		return Response(response_data, status=200)

	except Campaign.DoesNotExist:
		return Response({
			"error": f"Campaign with campaign_id='{campaign_id}' not found"
		}, status=404)
	except Exception as e:
		return Response({
			"error": f"An error occurred: {str(e)}"
		}, status=500)
	


#CODE FOR ACTUAL X API (can't be used due to rate limits on free plan)
# @api_view(['POST'])
# def createXPost(request):
# 	pk = request.data.get("pk")
# 	if not pk:
# 		return Response({"error": "Missing 'pk' field"}, status=400)

# 	post = Post.objects.get(pk=pk)

	
# 	if post.selected_variant:
# 		variant = ContentVariant.objects.filter(variant_id=post.selected_variant, post=post).first()
# 		text = variant.content if variant else post.description
# 	else:
		
# 		variant = ContentVariant.objects.filter(variant_id="A", post=post).first()
# 		text = variant.content if variant else post.description

# 	# Use clone API instead of real Twitter API
# 	url = f"http://api.x.com/2/tweets"
# 	headers = {
# 		"Content-Type": "application/json"
# 	}
# 	body = {"text": text}

# 	resp = requests.post(url, headers=headers, json=body)
# 	data = resp.json()

# 	if resp.status_code == 201:
# 		tweet_id = (data.get("data")).get("id")
# 		if tweet_id:
# 			postMetrics = post.metrics
# 			if postMetrics:
# 				postMetrics.tweet_id = tweet_id
# 				postMetrics.save()
# 			post.status = "published"
# 			post.save()

# 	return Response(resp.json(), status=resp.status_code)

# @api_view(['GET'])
# def getXPostMetrics(request):
	# url = "https://api.x.com/2/tweets"
	# headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}
	# params = {"ids": ",".join(tweet_ids[:100]), "tweet.fields": "public_metrics"}
	# return requests.get(url, headers=headers, params=params)
	