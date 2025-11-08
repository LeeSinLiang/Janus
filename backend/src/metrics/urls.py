from django.urls import path
from . import views

urlpatterns = [
    # path('metricsDisplay/', views.metricsDisplay, name='metricsDisplay'),
    path('metricsJson/', views.metricsJSON, name='metricsJson'),
    path('nodesJson/', views.nodesJSON, name='nodesJson'),
<<<<<<< HEAD
    path('createXPost/', views.createXPost, name='createXPost'),
=======
    path('api/approve', views.approveNode, name='approveNode'),
    path('api/graph', views.rejectNode, name='rejectNode'),
>>>>>>> 97ddd953283ae890f8cbe17553ee5a4c682f52af
]