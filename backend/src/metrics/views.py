from django.shortcuts import render
import os
import requests
from dotenv import load_dotenv
from django.conf import settings
from .models import PostMetrics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import PostMetricsSerializer, PostSerializer
from agents.models import Post, ContentVariant
from requests_oauthlib import OAuth1

auth = OAuth1(
    settings.X_API_KEY,
    settings.X_API_SECRET,
    settings.X_ACCESS_TOKEN,
    settings.X_ACCESS_TOKEN_SECRET,
)


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
    
    post = Post.objects.get(pk=pk)
    variantId = post.selected_variant
    selectedVariant = ContentVariant.objects.get(variant_id=variantId, post=post)
    text = selectedVariant.content

    url = "https://api.x.com/2/tweets"
    headers = {
        # "Authorization": f"Bearer {settings.X_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {"text": text}

    resp = requests.post(url, headers=headers, json=body, auth=auth)
    data = resp.json()

    if resp.status_code == 201:
        tweet_id = (data.get("data")).get("id")
        if tweet_id:
            postMetrics = post.metrics
            postMetrics.tweet_id = tweet_id
            post.status = "published"
            postMetrics.save()
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

    url = f"https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {settings.X_USER_BEARER_TOKEN}",  # <- user-context token
        "Content-Type": "application/json",
    }
    params = {
        "ids": tweet_id,
        "tweet.fields": "public_metrics,non_public_metrics"
    }
    
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()

    if resp.status_code == 200:
        d = data["data"][0]
        pub = d.get("public_metrics", {})
        nonpub = d.get("non_public_metrics", {})
        PostMetrics.objects.filter(tweet_id=tweet_id).update(
            likes=pub.get("like_count", 0),
            retweets=pub.get("retweet_count", 0),
            impressions=nonpub.get("impression_count", 0),
        )
        return Response(data, status=200)
    return Response({"error": data}, status=resp.status_code)

@api_view(['GET'])
def metricsJSON(request):
    qs = PostMetrics.objects.all()
    serializer = PostMetricsSerializer(qs, many=True)
    return Response(serializer.data)

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
