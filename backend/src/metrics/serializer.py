from rest_framework import serializers
from .models import PostMetrics
from agents.models import Post, ContentVariant

class PostMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetrics
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('pk', 'title', 'description', 'next_posts', 'phase')

    def get_description(self, obj):
        """Return selected variant's content if exists, otherwise return post description"""
        if obj.selected_variant:
            # Get the selected variant
            variant = obj.variants.filter(variant_id=obj.selected_variant).first()
            if variant:
                return variant.content
        # Fallback to post description
        return obj.description

class ContentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVariant
        fields = ('variant_id', 'content', 'platform', 'metadata')
