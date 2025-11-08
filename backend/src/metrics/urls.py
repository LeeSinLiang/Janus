from django.urls import path
from . import views

urlpatterns = [
    # path('metricsDisplay/', views.metricsDisplay, name='metricsDisplay'),
    path('metricsJson/', views.metricsJSON, name='metricsJson'),
    path('nodesJson/', views.nodesJSON, name='nodesJSON'),
    path('getVariants/', views.getVariants, name='getVariants'),
    path('selectVariant/', views.selectVariant, name='selectVariant'),
    path('createXPost/', views.createXPost, name='createXPost'),
    path('getXPostMetrics/', views.getXPostMetrics, name='getXPostMetrics'),
    path('api/approve', views.approveNode, name='approveNode'),
    path('api/graph', views.rejectNode, name='rejectNode'),
    path('createIGPost/', views.createIGPost, name='createIGPost'),
]