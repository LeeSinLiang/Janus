from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import NodeMetrics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import NodeMetricsSerializer


# Create your views here.
# def metricsDisplay(request):
#     nodes = NodeMetrics.objects.all().values()
#     template = loader.get_template('metricsDisplay.html')
#     context = {
#         'nodes': nodes,
#         'metricsJson': None,
#     }
#     return HttpResponse(template.render(context, request))

@api_view(['GET'])
def metricsJSON(request):
    qs = NodeMetrics.objects.all()
    serializer = NodeMetricsSerializer(qs, many=True)
    return Response(serializer.data) 