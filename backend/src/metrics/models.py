from django.db import models

# Create your models here.
class PostMetrics(models.Model):
    likes = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    tweet_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.post_set.first().post_id} Metrics"
    


