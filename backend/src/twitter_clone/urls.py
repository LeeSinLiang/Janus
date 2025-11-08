from django.urls import path
from . import views

urlpatterns = [
    # Twitter API v2 compatible endpoints
    path('2/tweets', views.create_tweet, name='clone_create_tweet'),  # POST
    path('2/tweets', views.get_tweets, name='clone_get_tweets'),  # GET (Django routes by method)

    # Additional actions
    path('2/tweets/like', views.like_tweet, name='clone_like_tweet'),
    path('2/tweets/retweet', views.retweet, name='clone_retweet'),
    path('2/tweets/comment', views.comment_on_tweet, name='clone_comment'),
]
