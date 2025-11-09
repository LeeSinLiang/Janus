"""
Serializers for Agents API
"""

from rest_framework import serializers
from .models import Campaign, Post, ContentVariant


class StrategyPlanningRequestSerializer(serializers.Serializer):
    """Serializer for strategy planning request"""
    product_description = serializers.CharField(
        required=True,
        help_text="Description of the product or service"
    )
    gtm_goals = serializers.CharField(
        required=True,
        help_text="Go-to-market goals and objectives"
    )
    campaign_name = serializers.CharField(
        required=False,
        default="GTM Campaign",
        help_text="Name for the campaign (optional)"
    )
    save_to_db = serializers.BooleanField(
        default=True,
        help_text="Whether to save the strategy to database (default: true)"
    )
    enable_video = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Enable video generation for first post variant (default: false)"
    )


class PostNodeSerializer(serializers.Serializer):
    """Serializer for post nodes in the strategy"""
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    phase = serializers.CharField()


class ConnectionSerializer(serializers.Serializer):
    """Serializer for connections between nodes"""
    from_node = serializers.CharField(source='from')
    to_node = serializers.CharField(source='to')


class StrategyPlanningResponseSerializer(serializers.Serializer):
    """Serializer for strategy planning response"""
    success = serializers.BooleanField()
    campaign_id = serializers.CharField(allow_null=True)
    mermaid_diagram = serializers.CharField()
    nodes = PostNodeSerializer(many=True)
    connections = ConnectionSerializer(many=True)
    total_posts = serializers.IntegerField()
    message = serializers.CharField()


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model"""
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id',
            'campaign_id',
            'name',
            'description',
            'phase',
            'strategy',
            'metadata',
            'insights',
            'posts_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_posts_count(self, obj):
        return obj.posts.count()


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    variants_count = serializers.SerializerMethodField()
    next_posts_ids = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'post_id',
            'campaign',
            'title',
            'description',
            'phase',
            'status',
            'selected_variant',
            'variants_count',
            'next_posts_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_variants_count(self, obj):
        return obj.variants.count()

    def get_next_posts_ids(self, obj):
        return list(obj.next_posts.values_list('post_id', flat=True))


class ContentVariantSerializer(serializers.ModelSerializer):
    """Serializer for ContentVariant model"""

    class Meta:
        model = ContentVariant
        fields = [
            'id',
            'post',
            'variant_id',
            'content',
            'platform',
            'status',
            'metadata',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
