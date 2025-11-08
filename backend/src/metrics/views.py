from django.shortcuts import render
<<<<<<< HEAD
from django.http import HttpResponse
from django.template import loader
=======
from django.views.decorators.csrf import csrf_exempt
>>>>>>> 97ddd953283ae890f8cbe17553ee5a4c682f52af
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
    settings.X_CONSUMER_KEY,
    settings.X_CONSUMER_SECRET,
    settings.X_ACCESS_TOKEN,
    settings.X_ACCESS_TOKEN_SECRET,
)



# Create your views here.
@api_view(['GET'])
def nodesJSON(request):
    qs = Post.objects.all()
    serializer = PostSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def metricsJSON(request):
    qs = PostMetrics.objects.all()
    serializer = PostMetricsSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createXPost(request):
    pk = request.data.get("pk")
    if not pk:
        return Response({"error": "Missing 'pk' field"}, status=400)
    
    variantId = Post.objects.get(pk=pk).selected_variant
    selectedVariant = ContentVariant.objects.get(variant_id=variantId, post=Post.objects.get(pk=pk))
    text = selectedVariant.content

    url = "https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {settings.X_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {"text": text}

    resp = requests.post(url, headers=headers, json=body)
    if resp.status_code == 201:
        return Response(resp.json(), status=201)
    else:
        return Response({"error": resp.json()}, status=resp.status_code)
    
@api_view(['GET'])
def getXPostMetrics(request, tweet_id):
    access_token = settings.X_ACCESS_TOKEN
    url = f"https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "ids": tweet_id,
        "tweet.fields": "public_metrics,non_public_metrics"
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return Response(resp.json(), status=200)
    else:
        return Response({"error": resp.json()}, status=resp.status_code)
<<<<<<< HEAD
    

    template = loader.get_template('createPost.html')
    return HttpResponse(template.render())
=======

@api_view(['POST'])
def approveNode(request):
    """Approve a pending node"""
    node_name = request.data.get("node_name")
    if not node_name:
        return Response({"error": "Missing 'node_name' field"}, status=400)

    # Find the post by title
    try:
        post = Post.objects.get(title=node_name)
        # Mark as approved (you can add an 'approved' field to the model later)
        # For now, just return success
        return Response({
            "success": True,
            "message": f"Node '{node_name}' approved",
            "post_id": post.pk
        }, status=200)
    except Post.DoesNotExist:
        return Response({
            "error": f"Post with title '{node_name}' not found"
        }, status=404)

@api_view(['POST'])
def rejectNode(request):
    """Reject a pending node and remove it"""
    node_name = request.data.get("node_name")
    reject_message = request.data.get("reject_message", "")

    if not node_name:
        return Response({"error": "Missing 'node_name' field"}, status=400)

    # Find the post by title
    try:
        post = Post.objects.get(title=node_name)
        post_id = post.pk
        # Delete the post
        post.delete()

        return Response({
            "success": True,
            "message": f"Node '{node_name}' rejected and removed",
            "reject_message": reject_message,
            "post_id": post_id
        }, status=200)
    except Post.DoesNotExist:
        return Response({
            "error": f"Post with title '{node_name}' not found"
        }, status=404)
>>>>>>> 97ddd953283ae890f8cbe17553ee5a4c682f52af
