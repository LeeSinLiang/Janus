"""
URL configuration for Agents API
"""

from django.urls import path
from .views import (
    StrategyPlanningAPIView,
    CampaignListAPIView,
    CampaignDetailAPIView,
    GenerateNewPostAPIView,
    RegenerateStrategyAPIView
)

app_name = 'agents'

urlpatterns = [
    # Strategy Planning API
    path('strategy/', StrategyPlanningAPIView.as_view(), name='strategy-planning'),

    # Campaign APIs
    path('campaigns/', CampaignListAPIView.as_view(), name='campaign-list'),
    path('campaigns/<str:campaign_id>/', CampaignDetailAPIView.as_view(), name='campaign-detail'),

    # New Post Generation API
    path('generate-new-post/', GenerateNewPostAPIView.as_view(), name='generate-new-post'),

    # Strategy Regeneration API
    path('regenerate-strategy/', RegenerateStrategyAPIView.as_view(), name='regenerate-strategy'),
]
