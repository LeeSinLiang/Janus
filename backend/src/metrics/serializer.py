from rest_framework import serializers
from .models import NodeMetrics

class NodeMetricsJSON(serializers.ModelSerializer):
    class Meta:
        model = NodeMetrics
        fields = '__all__'