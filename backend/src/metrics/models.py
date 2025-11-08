from django.db import models

# Create your models here.
class NodeMetrics(models.Model):
    node_id = models.BigAutoField(primary_key=True)
    likes = models.IntegerField()
    impressions = models.IntegerField()
    retweets = models.IntegerField()

    def __str__(self):
        return f"{self.node_id}"