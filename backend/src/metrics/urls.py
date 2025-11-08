from django.urls import path
from . import views

urlpatterns = [
    path('metricsDisplay', views.metricsDisplay, name='metricsDisplay'),
]