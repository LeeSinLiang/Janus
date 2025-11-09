from django.contrib import admin
from .models import Campaign, Post, ContentVariant, AgentMemory, ConversationMessage


class ContentVariantInline(admin.TabularInline):
    """Inline admin for content variants"""
    model = ContentVariant
    extra = 0
    fields = ('variant_id', 'content', 'platform', 'asset', 'metadata')
    readonly_fields = ('created_at',)


class PostInline(admin.TabularInline):
    """Inline admin for posts"""
    model = Post
    extra = 0
    fields = ('post_id', 'phase', 'status', 'selected_variant')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for Campaign model"""
    list_display = ('campaign_id', 'name', 'phase', 'created_at', 'updated_at')
    list_filter = ('phase', 'created_at')
    search_fields = ('campaign_id', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PostInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('campaign_id', 'name', 'description', 'phase')
        }),
        ('Strategy', {
            'fields': ('strategy',),
            'description': 'Mermaid diagram for campaign visualization'
        }),
        ('Insights & Metadata', {
            'fields': ('insights', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model"""
    list_display = ('pk', 'title', 'description', 'post_id', 'campaign', 'phase', 'status', 'selected_variant', 'created_at')
    list_filter = ('status', 'phase', 'created_at')
    search_fields = ('post_id', 'campaign__name', 'campaign__campaign_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ContentVariantInline]

    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'description', 'next_posts', 'post_id', 'campaign', 'phase', 'status', 'selected_variant', 'trigger')
        }),
        ('Metrics', {
            'fields': ('metrics',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentVariant)
class ContentVariantAdmin(admin.ModelAdmin):
    """Admin interface for ContentVariant model"""
    list_display = ('variant_id', 'post', 'asset', 'content_preview', 'created_at')
    list_filter = ('platform', 'created_at')
    search_fields = ('variant_id', 'content', 'post__post_id')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Variant Information', {
            'fields': ('variant_id', 'post', 'platform')
        }),
        ('Content', {
            'fields': ('content', 'asset')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        """Show preview of content"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(AgentMemory)
class AgentMemoryAdmin(admin.ModelAdmin):
    """Admin interface for AgentMemory model"""
    list_display = ('agent_name', 'updated_at', 'history_count')
    search_fields = ('agent_name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Agent Information', {
            'fields': ('agent_name',)
        }),
        ('Memory Data', {
            'fields': ('context', 'history'),
            'description': 'Agent context and history stored as JSON'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def history_count(self, obj):
        """Show count of history entries"""
        if isinstance(obj.history, list):
            return len(obj.history)
        return 0
    history_count.short_description = 'History Entries'


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    """Admin interface for ConversationMessage model"""
    list_display = ('role', 'content_preview', 'campaign', 'created_at')
    list_filter = ('role', 'created_at', 'campaign')
    search_fields = ('content', 'campaign__name')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Message Information', {
            'fields': ('role', 'content', 'campaign')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        """Show preview of message content"""
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content'
