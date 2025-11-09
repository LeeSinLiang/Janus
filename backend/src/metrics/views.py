from django.shortcuts import render
import os, requests, time
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



# Create your views here.
def getMetricsDB():
	posts = Post.objects.filter(status="published").select_related('metrics')
	out = {}
	for post in posts:
		m = getattr(post, "metrics", None)
		out[int(post.pk)] = {
			"likes": m.likes if m else 0,
			"comments": m.comments if m else 0,
			"retweets": m.retweets if m else 0,
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
	
	post.trigger = trigger
	post.save()

	return Response({"success": True, "post_id": post.pk, "trigger": post.trigger}, status=status.HTTP_200_OK)

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

@api_view(['GET'])
def checkTrigger(request):
	publishedPosts = Post.objects.filter(status="published").select_related('metrics').order_by('created_at')
	triggeredPosts = []
	for post in publishedPosts:
		if (post.trigger == "like"):
			if (post.metrics.likes >= 1):
				triggeredPosts.append(post.pk)
		elif (post.trigger == "retweet"):
			if (post.metrics.retweets >= 1):
				triggeredPosts.append(post.pk)
	
	if (triggeredPosts):
		print("Triggered posts:", triggeredPosts)
		# callSinAgentAPI(triggeredPosts)

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
		post_metrics.append({
			"pk": post.pk,
			"title": post.title,
			"description": post.description,
			"likes": m.likes if m else 0,
			"retweets": m.retweets if m else 0,
			"impressions": m.impressions if m else 0,
			"comments": m.comments if m else 0,
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

	
	if post.selected_variant:
		variant = ContentVariant.objects.filter(variant_id=post.selected_variant, post=post).first()
		text = variant.content if variant else post.description
	else:
		variant = ContentVariant.objects.filter(variant_id="B", post=post).first()
		text = variant.content if variant else post.description

	# Use clone API instead of real Twitter API
	url = f"http://localhost:8000/clone/2/tweets"
	headers = {
		"Content-Type": "application/json"
	}
	body = {"text": text}

	resp = requests.post(url, headers=headers, json=body)
	data = resp.json()

	if resp.status_code == 201:
		tweet_id = (data.get("data")).get("id")
		if tweet_id:
			postMetrics = post.metrics
			if postMetrics:
				postMetrics.tweet_id = tweet_id
				postMetrics.save()
			post.status = "published"
			post.save()

	return Response(resp.json(), status=resp.status_code)

@api_view(['POST'])
def getXPostMetrics(request):
	pk = request.data.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)

	post = Post.objects.get(pk=pk)
	postMetrics = post.metrics
	tweet_id = postMetrics.tweet_id

	# Use clone API instead of real Twitter API
	url = f"http://localhost:8000/clone/2/metrics/"
	headers = {
		"Content-Type": "application/json"
	}
	body = {"tweet_ids": tweet_id}

	resp = requests.post(url, headers=headers, json=body)
	data = resp.json()

	if resp.status_code != 200:
		return Response({"error": resp.text}, status=resp.status_code)
	
	data = resp.json()
	items = data.get("data") or []
	if not items:
		return Response({"error": "Tweet not found in clone API."}, status=404)

	d = items[0]
	pub = d.get("public_metrics", {})
	nonpub = d.get("non_public_metrics", {})

	retweetCount = pub.get("retweet_count")
	likeCount = pub.get("like_count")
	commentCount = pub.get("reply_count")
	impressionCount = nonpub.get("impression_count")
	commentList = CloneComment.objects.filter(tweet__tweet_id=tweet_id).order_by('-created_at').values_list('text', flat=True)

	postMetrics.retweets = retweetCount
	postMetrics.likes = likeCount
	postMetrics.impressions = impressionCount
	postMetrics.comments = commentCount
	postMetrics.commentList = list(commentList)
	postMetrics.save()

	return Response(resp.json(), status=resp.status_code)

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
		# Verify the variant exists
		variant = post.variants.filter(variant_id=variant_id).first()

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

		# Approve each draft post and create X post
		for post in draft_posts:
			try:
				# Get the selected variant or default to variant A
				if post.selected_variant:
					variant = ContentVariant.objects.filter(variant_id=post.selected_variant, post=post).first()
					text = variant.content if variant else post.description
				else:
					variant = ContentVariant.objects.filter(variant_id="A", post=post).first()
					text = variant.content if variant else post.description

				# Create X post via clone API
				url = "http://localhost:8000/clone/2/tweets"
				headers = {"Content-Type": "application/json"}
				body = {"text": text}

				resp = requests.post(url, headers=headers, json=body)

				if resp.status_code == 201:
					data = resp.json()
					tweet_id = data.get("data", {}).get("id")

					if tweet_id:
						# Update post metrics with tweet_id
						post_metrics = post.metrics
						if post_metrics:
							post_metrics.tweet_id = tweet_id
							post_metrics.save()

					# Update post status to published
					post.status = 'published'
					post.save()
					approved_count += 1
				else:
					failed_posts.append({"post_id": post.pk, "title": post.title, "error": "Failed to create X post"})

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
	