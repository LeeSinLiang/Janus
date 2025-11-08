from django.shortcuts import render
import os, requests, time
from dotenv import load_dotenv
from django.conf import settings
from .models import PostMetrics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import PostMetricsSerializer, PostSerializer, ContentVariantSerializer
from agents.models import Post, ContentVariant, Campaign
from requests_oauthlib import OAuth1
from time import time
from django.core.cache import cache


CACHE_TTL = 120
def should_skip_fetch(tweet_id):
	key = f"x:last-fetch:{tweet_id}"
	last = cache.get(key)
	if last and time() - last < CACHE_TTL:
		return True
	cache.set(key, time(), CACHE_TTL)
	return False

auth = OAuth1(
	settings.X_API_KEY,
	settings.X_API_SECRET,
	settings.X_ACCESS_TOKEN,
	settings.X_ACCESS_TOKEN_SECRET,
)

POLL_TIMEOUT_SEC = 30
POLL_INTERVAL_SEC = 1.0
GRAPH_VERSION = "v23.0"


# Create your views here.
@api_view(['GET'])
def nodesJSON(request):
	qs = Post.objects.filter(campaign=Campaign.objects.first())
	serializer = PostSerializer(qs, many=True)
	return Response(serializer.data)

@api_view(['POST'])
def createXPost(request):
	pk = request.data.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)

	try:
		post = Post.objects.get(pk=pk)
	except Post.DoesNotExist:
		return Response({"error": f"Post with pk={pk} not found"}, status=404)

	# Determine content to post
	variantId = post.selected_variant
	if variantId:
		# Use selected variant if it exists
		try:
			selectedVariant = ContentVariant.objects.get(variant_id=variantId, post=post)
			text = selectedVariant.content
		except ContentVariant.DoesNotExist:
			return Response({"error": f"Selected variant '{variantId}' not found"}, status=404)
	else:
		# Fallback to post description if no variant selected
		text = post.description
		if not text:
			return Response({"error": "No content available to post (no variant or description)"}, status=400)

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
	url = f"http://localhost:8000/clone/2/tweets"
	headers = {
		"Content-Type": "application/json",
	}
	params = {
		"ids": tweet_id,
		"tweet.fields": "public_metrics"
	}

	resp = requests.get(url, headers=headers, params=params)
	data = resp.json()

	if resp.status_code == 200:
		d = data["data"][0]
		pub = d.get("public_metrics", {})
		postMetrics.likes = pub.get("like_count", 0)
		postMetrics.retweets = pub.get("retweet_count", 0)
		postMetrics.save()
		return Response(data, status=200)
	return Response({"error": data}, status=resp.status_code)

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




########################################################################
#                               INSTAGRAM
#########################################################################
def createIGPost(request):
	pk = request.data.get("pk")
	if not pk:
		return Response({"error": "Missing 'pk' field"}, status=400)
	
	post = Post.objects.get(pk=pk)
	variantId = post.selected_variant
	selectedVariant = ContentVariant.objects.get(variant_id=variantId, post=post)
	text = selectedVariant.content

