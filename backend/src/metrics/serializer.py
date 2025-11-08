from rest_framework import serializers
from .models import PostMetrics

class PostMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetrics
        fields = '__all__'