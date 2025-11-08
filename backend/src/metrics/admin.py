from django.contrib import admin

from metrics.models import PostMetrics, IGMetrics

# Register your models here.
class XAdmin(admin.ModelAdmin):
    list_display = ('pk', 'likes', 'retweets')

class IGAdmin(admin.ModelAdmin):
    list_display = ('pk', 'likes', 'shares')

admin.site.register(PostMetrics, XAdmin)
admin.site.register(IGMetrics, IGAdmin)