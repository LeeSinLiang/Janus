from rest_framework import serializers
from .models import CloneTweet, CloneLike, CloneRetweet, CloneComment


class TwitterAPIv2TweetSerializer(serializers.ModelSerializer):
    """Serializer that matches Twitter API v2 response format exactly"""

    id = serializers.CharField(source='tweet_id', read_only=True)
    author_id = serializers.CharField(source='author.id', read_only=True)

    # Metrics objects
    public_metrics = serializers.SerializerMethodField()
    non_public_metrics = serializers.SerializerMethodField()

    class Meta:
        model = CloneTweet
        fields = ['id', 'text', 'created_at', 'author_id', 'public_metrics', 'non_public_metrics']

    def get_public_metrics(self, obj):
        """Return public metrics in Twitter API v2 format"""
        return {
            "retweet_count": obj.get_retweet_count(),
            "reply_count": obj.get_reply_count(),
            "like_count": obj.get_like_count(),
            "quote_count": 0,  # Not implemented for MVP
        }

    def get_non_public_metrics(self, obj):
        """Return non-public metrics in Twitter API v2 format"""
        return {
            "impression_count": obj.get_impression_count(),
            "user_profile_clicks": 0,  # Not implemented for MVP
        }


class TwitterAPIv2CreateTweetSerializer(serializers.Serializer):
    """Serializer for creating tweets - matches Twitter API v2 POST /2/tweets request"""

    text = serializers.CharField(max_length=280)
    media = serializers.ImageField(required=False, allow_null=True)
    media_video = serializers.FileField(required=False, allow_null=True)

    def create(self, validated_data):
        """Create a new tweet"""
        media = validated_data.pop('media', None)
        media_video = validated_data.pop('media_video', None)

        tweet = CloneTweet.objects.create(**validated_data)

        # Handle media
        if media:
            tweet.media_image = media
            tweet.media_type = 'image'
        elif media_video:
            tweet.media_video = media_video
            tweet.media_type = 'video'

        tweet.save()
        return tweet


class TwitterAPIv2TweetResponseSerializer(serializers.ModelSerializer):
    """Serializer for POST /2/tweets response - simple id and text only"""

    id = serializers.CharField(source='tweet_id', read_only=True)

    class Meta:
        model = CloneTweet
        fields = ['id', 'text']
