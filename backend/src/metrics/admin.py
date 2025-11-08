from django.contrib import admin
from .models import NodeMetrics

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = ('node_id', 'likes', 'impressions', 'retweets')

admin.site.register(NodeMetrics, MemberAdmin)