from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import NodeMetrics
from .serializer import NodeMetricsJSON

# Create your views here.
def metricsDisplay(request):
    nodes = NodeMetrics.objects.all().values()
    template = loader.get_template('metricsDisplay.html')
    context = {
        'nodes': nodes,
        'metricsJson': None,
    }
    return HttpResponse(template.render(context, request))