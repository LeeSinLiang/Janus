from django.contrib import admin
from .models import NodeMetrics

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = ('pk', 'likes', 'impressions', 'retweets')

admin.site.register(NodeMetrics, MemberAdmin)