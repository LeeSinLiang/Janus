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
    has_trigger = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('pk', 'title', 'description', 'next_posts', 'phase', 'status', 'has_trigger')

    def get_has_trigger(self, obj):
        return obj.trigger_condition is not None

class ContentVariantSerializer(serializers.ModelSerializer):
    asset = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ContentVariant
        fields = ('variant_id', 'content', 'platform', 'metadata', 'asset')
