from django.db import models

# Create your models here.
class PostMetrics(models.Model):
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    tweet_id = models.CharField(max_length=50)

    def __str__(self):
        post = self.post_set.first()
        if post and post.post_id:
            return f"{post.post_id} X Metrics"
        return f"XMetrics #{self.pk}"
    

class IGMetrics(models.Model):
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    post_id = models.CharField(max_length=50)

    def __str__(self):
        post = self.post_set.first()
        if post and post.post_id:
            return f"{post.post_id} IG Metrics"
        return f"IGMetrics #{self.pk}"


