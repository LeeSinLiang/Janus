from django.contrib import admin
from .models import CloneTweet, CloneLike, CloneRetweet, CloneComment, CloneImpression


@admin.register(CloneTweet)
class CloneTweetAdmin(admin.ModelAdmin):
    list_display = ['tweet_id', 'text', 'author', 'media_type', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['tweet_id', 'text']
    readonly_fields = ['tweet_id', 'created_at']


@admin.register(CloneLike)
class CloneLikeAdmin(admin.ModelAdmin):
    list_display = ['tweet', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tweet__tweet_id']


@admin.register(CloneRetweet)
class CloneRetweetAdmin(admin.ModelAdmin):
    list_display = ['original_tweet', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['original_tweet__tweet_id']


@admin.register(CloneComment)
class CloneCommentAdmin(admin.ModelAdmin):
    list_display = ['tweet', 'user', 'text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tweet__tweet_id', 'text']


@admin.register(CloneImpression)
class CloneImpressionAdmin(admin.ModelAdmin):
    list_display = ['tweet', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tweet__tweet_id']
