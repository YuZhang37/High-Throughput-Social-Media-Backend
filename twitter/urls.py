"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pprint import pprint

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from friendships.api.views import FriendshipViewSet
from tweets.api.views import TweetViewSet

admin.site.site_header = 'Twitter Admin'
# The text to put at the top of the admin index page (a string).
# By default, this is “Site administration”.
admin.site.index_title = 'Admin'

router = routers.DefaultRouter()
router.register('tweets', TweetViewSet, basename='tweet')
router.register('friendships', FriendshipViewSet, basename='friendship')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('core/', include('core.urls')),
    path('playground/', include('playground.urls')),
    path('api/', include(router.urls)),

]
