from django.contrib import admin
from metrics.models import PostMetrics

# Register your models here.
class XAdmin(admin.ModelAdmin):
    list_display = ('pk', 'likes', 'retweets', 'impressions', 'comments', 'tweet_id')

admin.site.register(PostMetrics, XAdmin)