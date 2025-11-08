from django.db import models
from agents.models import Post

# Create your models here.
class PostMetrics(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    tweet_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.post.pk}"