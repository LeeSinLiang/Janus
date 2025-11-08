from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import NodeMetrics
from .serializer import NodeMetricsJSON

@api_view(['GET'])
def getNodeMetrics(request):
    return Response(NodeMetricsJSON({'node_id': 1, 'likes': 100, 'impressions': 200, 'retweets': 50}))
