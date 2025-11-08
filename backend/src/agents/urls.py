"""
URL configuration for Agents API
"""

from django.urls import path
from .views import (
    StrategyPlanningAPIView,
    CampaignListAPIView,
    CampaignDetailAPIView
)

app_name = 'agents'

urlpatterns = [
    # Strategy Planning API
    path('strategy/', StrategyPlanningAPIView.as_view(), name='strategy-planning'),

    # Campaign APIs
    path('campaigns/', CampaignListAPIView.as_view(), name='campaign-list'),
    path('campaigns/<str:campaign_id>/', CampaignDetailAPIView.as_view(), name='campaign-detail'),
]
