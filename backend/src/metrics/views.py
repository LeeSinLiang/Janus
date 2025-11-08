from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import NodeMetrics

# Create your views here.
def nodeMetricsDisplay(request, nodeId):
    node = NodeMetrics.objects.get(node_id=nodeId)
    template = loader.get_template('metricsDisplay.html')
    context = {
        'node_id': node.node_id,
        'likes': node.likes,
        'impressions': node.impressions,
        'retweets': node.retweets,
    }
    return HttpResponse(template.render(context, request))