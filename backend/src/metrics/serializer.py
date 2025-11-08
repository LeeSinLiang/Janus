from rest_framework import serializers
from .models import PostMetrics, IGMetrics
from agents.models import Post

class PostMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetrics
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('pk', 'title', 'description', 'next_posts', 'phase')

class IGMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IGMetrics
        fields = '__all__'

