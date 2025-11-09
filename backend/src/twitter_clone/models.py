from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CloneTweet(models.Model):
    """Twitter clone tweet model - mimics Twitter API v2 tweet structure"""

    # Twitter uses snowflake IDs (19-digit numbers), we'll auto-generate
    tweet_id = models.CharField(max_length=50, unique=True, db_index=True)

    # Tweet content
    text = models.TextField(max_length=280)  # Twitter's character limit

    # Author (for simplicity, we'll use Django's built-in User model)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tweets',
        default=1  # Default user ID
    )

    # Media attachments (images/videos)
    media_image = models.ImageField(upload_to='tweets/images/', null=True, blank=True)
    media_video = models.FileField(upload_to='tweets/videos/', null=True, blank=True)
    media_type = models.CharField(
        max_length=10,
        choices=[('image', 'Image'), ('video', 'Video'), ('text', 'Text Only')],
        default='text'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    # For threading (replies)
    in_reply_to_tweet_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tweet_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Tweet {self.tweet_id}: {self.text[:50]}"

    # Calculate metrics on-demand
    def get_like_count(self):
        return self.likes.count()

    def get_retweet_count(self):
        return self.retweets.count()

    def get_reply_count(self):
        return self.comments.count()

    def get_impression_count(self):
        # For MVP, impressions = likes + retweets + replies + base views
        # We'll track this with a simple counter that increments on each view
        return self.impressions.count()

    def save(self, *args, **kwargs):
        # Auto-generate tweet_id if not provided (simplified snowflake ID)
        if not self.tweet_id:
            import time
            timestamp = int(time.time() * 1000)  # milliseconds
            self.tweet_id = str(timestamp)
        super().save(*args, **kwargs)


class CloneLike(models.Model):
    """Track likes on tweets"""

    tweet = models.ForeignKey(
        CloneTweet,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tweet', 'user']  # User can only like a tweet once
        indexes = [
            models.Index(fields=['tweet', 'user']),
        ]

    def __str__(self):
        return f"Like on {self.tweet.tweet_id} by {self.user.username}"


class CloneRetweet(models.Model):
    """Track retweets"""

    original_tweet = models.ForeignKey(
        CloneTweet,
        on_delete=models.CASCADE,
        related_name='retweets'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['original_tweet', 'user']  # User can only retweet once
        indexes = [
            models.Index(fields=['original_tweet', 'user']),
        ]

    def __str__(self):
        return f"Retweet of {self.original_tweet.tweet_id} by {self.user.username}"


class CloneComment(models.Model):
    """Track comments/replies on tweets"""

    tweet = models.ForeignKey(
        CloneTweet,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1
    )
    text = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tweet', '-created_at']),
        ]

    def __str__(self):
        return f"Comment on {self.tweet.tweet_id}: {self.text[:50]}"


class CloneImpression(models.Model):
    """Track impressions (views) on tweets - simplified tracking"""

    tweet = models.ForeignKey(
        CloneTweet,
        on_delete=models.CASCADE,
        related_name='impressions'
    )
    # In a real system, you'd track IP, session, etc. For simplicity, just count
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['tweet']),
        ]

    def __str__(self):
        return f"Impression on {self.tweet.tweet_id}"
