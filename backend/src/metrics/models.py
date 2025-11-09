from django.db import models

# Create your models here.
class PostMetrics(models.Model):
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    commentList = models.JSONField(default=list)
    tweet_id = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        post = self.post_set.first()
        if post and post.post_id:
            return f"{post.post_id} X Metrics"
        return f"XMetrics #{self.pk}"