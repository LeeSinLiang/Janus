from django.db import models
from agents.models import Post

# Create your models here.
class NodeMetrics(models.Model):
    node_id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    likes = models.IntegerField()
    impressions = models.IntegerField()
    retweets = models.IntegerField()

    def __str__(self):
        return f"{self.node_id}"