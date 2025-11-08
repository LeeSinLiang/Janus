from django.db import models
from agents.models import Post

# Create your models here.
class NodeMetrics(models.Model):
    post_id = models.ForeignKey(Post.post_id, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    node_id = models.IntegerField()

    def __str__(self):
        return f"{self.pk}"
    
    # generate random node_id
    def save(self, *args, **kwargs):
        if not self.node_id:
            import random
            self.node_id = random.randint(1, 1000000)
        super().save(*args, **kwargs)


class Node(models.Model):
    node_id = models.IntegerField(primary_key=True)
    

    def __str__(self):
        return self.name