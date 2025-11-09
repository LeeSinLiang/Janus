from django.db import models

# Create your models here.
class PostMetrics(models.Model):
    # A/B variant metrics stored as JSON: {"A": value, "B": value}
    likes = models.JSONField(default=dict)
    retweets = models.JSONField(default=dict)
    impressions = models.JSONField(default=dict)
    comments = models.JSONField(default=dict)
    commentList = models.JSONField(default=dict)  # {"A": [...], "B": [...]}
    tweet_id = models.JSONField(default=dict)  # {"A": "123", "B": "456"}

    def __str__(self):
        post = self.post_set.first()
        if post and post.post_id:
            return f"{post.post_id} X Metrics"
        return f"XMetrics #{self.pk}"

    def get_variant_metrics(self, variant='A'):
        """Get metrics for a specific variant (A or B)"""
        return {
            'likes': self.likes.get(variant, 0) if isinstance(self.likes, dict) else 0,
            'retweets': self.retweets.get(variant, 0) if isinstance(self.retweets, dict) else 0,
            'impressions': self.impressions.get(variant, 0) if isinstance(self.impressions, dict) else 0,
            'comments': self.comments.get(variant, 0) if isinstance(self.comments, dict) else 0,
        }

    def get_max_metrics(self):
        """Get maximum metrics across both variants for canvas display"""
        if not isinstance(self.likes, dict):
            return {'likes': 0, 'retweets': 0, 'impressions': 0, 'comments': 0}

        return {
            'likes': max(self.likes.get('A', 0), self.likes.get('B', 0)),
            'retweets': max(self.retweets.get('A', 0), self.retweets.get('B', 0)),
            'impressions': max(self.impressions.get('A', 0), self.impressions.get('B', 0)),
            'comments': max(self.comments.get('A', 0), self.comments.get('B', 0)),
        }

    def get_aggregated_metrics(self):
        """Get sum of metrics across both variants for chart view"""
        if not isinstance(self.likes, dict):
            return {'likes': 0, 'retweets': 0, 'impressions': 0, 'comments': 0}

        return {
            'likes': self.likes.get('A', 0) + self.likes.get('B', 0),
            'retweets': self.retweets.get('A', 0) + self.retweets.get('B', 0),
            'impressions': self.impressions.get('A', 0) + self.impressions.get('B', 0),
            'comments': self.comments.get('A', 0) + self.comments.get('B', 0),
        }