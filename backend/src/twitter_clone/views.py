from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import CloneTweet, CloneLike, CloneRetweet, CloneComment, CloneImpression
from .serializers import (
    TwitterAPIv2TweetSerializer,
    TwitterAPIv2CreateTweetSerializer,
    TwitterAPIv2TweetResponseSerializer
)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_tweet(request):
    """
    POST /clone/2/tweets

    Mimics Twitter API v2 POST /2/tweets endpoint
    Accepts: text (required), media (optional), media_video (optional)
    Returns: {"data": {"id": "...", "text": "..."}}
    """
    serializer = TwitterAPIv2CreateTweetSerializer(data=request.data)

    if serializer.is_valid():
        # Get or create default user
        user, _ = User.objects.get_or_create(
            id=1,
            defaults={'username': 'default_user', 'email': 'default@example.com'}
        )

        # Create tweet
        tweet = serializer.save(author=user)

        # Return response in Twitter API v2 format
        response_serializer = TwitterAPIv2TweetResponseSerializer(tweet)
        return Response(
            {"data": response_serializer.data},
            status=status.HTTP_201_CREATED
        )

    return Response(
        {"errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
def get_tweets(request):
    """
    GET /clone/2/tweets

    Mimics Twitter API v2 GET /2/tweets endpoint
    Query params:
    - ids: Comma-separated tweet IDs
    - tweet.fields: Comma-separated field names (e.g., "public_metrics,non_public_metrics")

    Returns: {"data": [{...tweet objects...}]}
    """
    # Get tweet IDs from query params
    tweet_ids = request.GET.get('ids', '')
    if not tweet_ids:
        return Response(
            {"errors": [{"message": "Missing required parameter: ids"}]},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Split comma-separated IDs
    ids_list = [id.strip() for id in tweet_ids.split(',')]

    # Get tweets
    tweets = CloneTweet.objects.filter(tweet_id__in=ids_list)

    if not tweets.exists():
        return Response(
            {"errors": [{"message": "Tweet not found"}]},
            status=status.HTTP_404_NOT_FOUND
        )

    # Track impressions for each tweet viewed
    for tweet in tweets:
        CloneImpression.objects.create(tweet=tweet)

    # Serialize tweets in Twitter API v2 format
    serializer = TwitterAPIv2TweetSerializer(tweets, many=True)

    return Response(
        {"data": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def like_tweet(request):
    """
    POST /clone/2/tweets/:id/like

    Like a tweet
    Body: {"tweet_id": "..."}
    """
    tweet_id = request.data.get('tweet_id')
    if not tweet_id:
        return Response(
            {"error": "Missing tweet_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tweet = CloneTweet.objects.get(tweet_id=tweet_id)
    except CloneTweet.DoesNotExist:
        return Response(
            {"error": "Tweet not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Create like (or get existing)
    like, created = CloneLike.objects.get_or_create(tweet=tweet, user=user)

    return Response(
        {"success": True, "created": created},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def retweet(request):
    """
    POST /clone/2/tweets/:id/retweet

    Retweet a tweet
    Body: {"tweet_id": "..."}
    """
    tweet_id = request.data.get('tweet_id')
    if not tweet_id:
        return Response(
            {"error": "Missing tweet_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tweet = CloneTweet.objects.get(tweet_id=tweet_id)
    except CloneTweet.DoesNotExist:
        return Response(
            {"error": "Tweet not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Create retweet (or get existing)
    retweet, created = CloneRetweet.objects.get_or_create(
        original_tweet=tweet,
        user=user
    )

    return Response(
        {"success": True, "created": created},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def comment_on_tweet(request):
    """
    POST /clone/2/tweets/:id/comment

    Comment on a tweet
    Body: {"tweet_id": "...", "text": "..."}
    """
    tweet_id = request.data.get('tweet_id')
    text = request.data.get('text')

    if not tweet_id or not text:
        return Response(
            {"error": "Missing tweet_id or text"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tweet = CloneTweet.objects.get(tweet_id=tweet_id)
    except CloneTweet.DoesNotExist:
        return Response(
            {"error": "Tweet not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Create comment
    comment = CloneComment.objects.create(
        tweet=tweet,
        user=user,
        text=text
    )

    return Response(
        {
            "success": True,
            "comment_id": comment.id,
            "text": comment.text
        },
        status=status.HTTP_201_CREATED
    )
