from django.contrib import admin
from metrics.models import PostMetrics

# Register your models here.
class XAdmin(admin.ModelAdmin):
    list_display = ('pk', 'likes', 'retweets')

admin.site.register(PostMetrics, XAdmin)