from rest_framework import serializers
from .models import PostMetrics
from agents.models import Post
from .models import PostMetrics
from agents.models import Post, ContentVariant

class PostMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetrics
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    assets_ready = serializers.SerializerMethodField()
    has_trigger = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('pk', 'title', 'description', 'next_posts', 'phase', 'status', 'assets_ready', 'has_trigger')

    def get_has_trigger(self, obj):
        return obj.trigger_condition is not None
    def get_assets_ready(self, obj):
        """Check if both variant A and B have assets (images) ready"""
        try:
            variant_a = ContentVariant.objects.filter(post=obj, variant_id='A').order_by('-created_at').first()
            variant_b = ContentVariant.objects.filter(post=obj, variant_id='B').order_by('-created_at').first()

            # Both variants must exist and have assets
            if variant_a and variant_b:
                return bool(variant_a.asset) and bool(variant_b.asset)
            return False
        except Exception:
            return False

class ContentVariantSerializer(serializers.ModelSerializer):
    asset = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ContentVariant
        fields = ('variant_id', 'content', 'platform', 'metadata', 'asset', 'created_at')
