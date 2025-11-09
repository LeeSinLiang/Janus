from debug import debug_print
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from agents.models import Post
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage

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
    text = request.data.get('text', '')
    media = request.data.get('media')

    user, _ = User.objects.get_or_create(id=1, defaults={'username': 'default_user'})
    tweet = CloneTweet.objects.create(text=text, author=user)
    debug_print(f"{user} created tweet {tweet.tweet_id} with text: {text}")
    if media:
        if not default_storage.exists(media):
            return Response({"errors": {"media": [f"File not found: {media}"]}},
                            status=status.HTTP_400_BAD_REQUEST)

        low = media.lower()
        if low.endswith(".png"):
            tweet.media_image.name = media   # point field to existing file
            tweet.media_type = 'image'
        elif low.endswith(".mp4"):
            tweet.media_video.name = media
            tweet.media_type = 'video'
        else:
            return Response({"errors": {"media": ["Unsupported file extension."]}},
                            status=status.HTTP_400_BAD_REQUEST)

        tweet.save()

    return Response({"data": {"id": tweet.tweet_id, "text": tweet.text}}, status=status.HTTP_201_CREATED)
    # serializer = TwitterAPIv2CreateTweetSerializer(data=request.data)

    # if serializer.is_valid():
    #     # Get or create default user
    #     user, _ = User.objects.get_or_create(
    #         id=1,
    #         defaults={'username': 'default_user', 'email': 'default@example.com'}
    #     )

    #     # Create tweet
    #     tweet = serializer.save(author=user)

    #     # Return response in Twitter API v2 format
    #     response_serializer = TwitterAPIv2TweetResponseSerializer(tweet)
    #     return Response(
    #         {"data": response_serializer.data},
    #         status=status.HTTP_201_CREATED
    #     )

    # return Response(
    #     {"errors": serializer.errors},
    #     status=status.HTTP_400_BAD_REQUEST
    # )


@api_view(['POST'])
def get_tweets(request):
    """
    GET /clone/2/tweets

    Mimics Twitter API v2 GET /2/tweets endpoint
    Query params:
    - ids: Comma-separated tweet IDs
    - tweet.fields: Comma-separated field names (e.g., "public_metrics,non_public_metrics")

    Returns: {"data": [{...tweet objects...}]}
    """
    # Get tweet IDs
    tweet_ids = request.data.get("tweet_ids")
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


# ============================================================================
# Template-based views (HTML UI)
# ============================================================================

def home(request):
    """
    Home page showing all tweets in reverse chronological order
    """
    tweets = CloneTweet.objects.all().select_related('author').order_by('-created_at')

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Add helper properties to each tweet
    for tweet in tweets:
        tweet.is_liked = CloneLike.objects.filter(tweet=tweet, user=user).exists()
        tweet.is_retweeted = CloneRetweet.objects.filter(original_tweet=tweet, user=user).exists()

    return render(request, 'twitter_clone/home.html', {'tweets': tweets})


@require_http_methods(["GET", "POST"])
def create_tweet_page(request):
    """
    Page with form to create a new tweet
    """
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        media = request.FILES.get('media')
        media_video = request.FILES.get('media_video')

        if not text:
            return render(request, 'twitter_clone/create_tweet.html', {
                'error': 'Tweet text is required!'
            })

        if len(text) > 280:
            return render(request, 'twitter_clone/create_tweet.html', {
                'error': 'Tweet must be 280 characters or less!'
            })

        # Get or create default user
        user, _ = User.objects.get_or_create(
            id=1,
            defaults={'username': 'default_user', 'email': 'default@example.com'}
        )

        # Create tweet
        tweet = CloneTweet.objects.create(
            text=text,
            author=user
        )

        # Handle media
        if media:
            tweet.media_image = media
            tweet.media_type = 'image'
            tweet.save()
        elif media_video:
            tweet.media_video = media_video
            tweet.media_type = 'video'
            tweet.save()

        return redirect('clone_home')

    return render(request, 'twitter_clone/create_tweet.html')


def tweet_detail(request, tweet_id):
    """
    Detail page for a single tweet with comments
    """
    tweet = get_object_or_404(CloneTweet, tweet_id=tweet_id)
    comments = CloneComment.objects.filter(tweet=tweet).select_related('user').order_by('-created_at')

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Track impression
    CloneImpression.objects.create(tweet=tweet)

    # Check if user has liked/retweeted
    is_liked = CloneLike.objects.filter(tweet=tweet, user=user).exists()
    is_retweeted = CloneRetweet.objects.filter(original_tweet=tweet, user=user).exists()

    success_message = None
    error = None

    # Handle comment submission
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text', '').strip()

        if not comment_text:
            error = 'Comment text is required!'
        elif len(comment_text) > 280:
            error = 'Comment must be 280 characters or less!'
        else:
            CloneComment.objects.create(
                tweet=tweet,
                user=user,
                text=comment_text
            )
            success_message = 'Comment added successfully!'
            # Refresh comments
            comments = CloneComment.objects.filter(tweet=tweet).select_related('user').order_by('-created_at')

    return render(request, 'twitter_clone/tweet_detail.html', {
        'tweet': tweet,
        'comments': comments,
        'is_liked': is_liked,
        'is_retweeted': is_retweeted,
        'success_message': success_message,
        'error': error
    })


@require_http_methods(["POST"])
def like_tweet_ui(request, tweet_id):
    """
    Like a tweet (from UI form submission)
    """
    tweet = get_object_or_404(CloneTweet, tweet_id=tweet_id)

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Toggle like
    existing_like = CloneLike.objects.filter(tweet=tweet, user=user).first()
    if existing_like:
        existing_like.delete()
    else:
        CloneLike.objects.create(tweet=tweet, user=user)

    # Return to previous page
    return redirect(request.META.get('HTTP_REFERER', 'clone_home'))


@require_http_methods(["POST"])
def retweet_ui(request, tweet_id):
    """
    Retweet a tweet (from UI form submission)
    """
    tweet = get_object_or_404(CloneTweet, tweet_id=tweet_id)

    # Get or create default user
    user, _ = User.objects.get_or_create(
        id=1,
        defaults={'username': 'default_user', 'email': 'default@example.com'}
    )

    # Toggle retweet
    existing_retweet = CloneRetweet.objects.filter(original_tweet=tweet, user=user).first()
    if existing_retweet:
        existing_retweet.delete()
    else:
        CloneRetweet.objects.create(original_tweet=tweet, user=user)

    # Return to previous page
    return redirect(request.META.get('HTTP_REFERER', 'clone_home'))
