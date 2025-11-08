from django.db import models

# Create your models here.
class NodeMetrics(models.Model):
    node_id = models.IntegerField()
    likes = models.IntegerField()
    impressions = models.IntegerField()
    retweets = models.IntegerField()

    # def __str__(self):
        # return f"{self.id}. {self.firstName} {self.lastName}"