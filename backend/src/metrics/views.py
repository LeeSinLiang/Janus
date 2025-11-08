from django.shortcuts import render
import os
import requests
from dotenv import load_dotenv
from django.conf import settings
from .models import PostMetrics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import PostMetricsSerializer, PostSerializer
from agents.models import Post



# Create your views here.
@api_view(['GET'])
def metricsJSON(request):
    qs = PostMetrics.objects.all()
    serializer = PostMetricsSerializer(qs, many=True)
    return Response(serializer.data) 

@api_view(['GET'])
def nodesJSON(request):
    qs = Post.objects.all()
    serializer = PostSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createXPost(request):
    text = request.data.get("text")
    if not text:
        return Response({"error": "Missing 'text' field"}, status=400)

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