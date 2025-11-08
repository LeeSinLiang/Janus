from rest_framework import serializers
from .models import NodeMetrics

class NodeMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeMetrics
        fields = '__all__'