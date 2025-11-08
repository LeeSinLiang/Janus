from django.contrib import admin

from metrics.models import PostMetrics

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = ('pk', 'likes', 'impressions', 'retweets')

admin.site.register(PostMetrics, MemberAdmin)