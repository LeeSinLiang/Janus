from django.urls import path
from . import views

urlpatterns = [
    # Twitter API v2 compatible endpoints (for API calls)
    # path('2/tweets', views.create_tweet, name='clone_create_tweet'),  # POST
    # path('2/tweets', views.get_tweets, name='clone_get_tweets'),  # GET (Django routes by method)
    path('2/tweets', views.create_tweet, name='clone_create_tweet'),  # POST
    path('2/metrics/', views.get_tweets, name='clone_get_tweets'),  # GET (Django routes by method)

    # Additional API actions
    path('2/tweets/like', views.like_tweet, name='clone_like_tweet'),
    path('2/tweets/retweet', views.retweet, name='clone_retweet'),
    path('2/tweets/comment', views.comment_on_tweet, name='clone_comment'),

    # Template-based UI views (for web interface)
    path('', views.home, name='clone_home'),
    path('create/', views.create_tweet_page, name='clone_create_tweet_page'),
    path('tweet/<str:tweet_id>/', views.tweet_detail, name='clone_tweet_detail'),
    path('tweet/<str:tweet_id>/like/', views.like_tweet_ui, name='clone_like_tweet_ui'),
    path('tweet/<str:tweet_id>/retweet/', views.retweet_ui, name='clone_retweet_ui'),
]
