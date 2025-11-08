from django.urls import path
from . import views

urlpatterns = [
    path('nodeMetricsDisplay', views.nodeMetricsDisplay, name='nodeMetricsDisplay'),
]