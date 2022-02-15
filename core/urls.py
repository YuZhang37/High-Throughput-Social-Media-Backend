from django.urls import path, include
from rest_framework import routers

from core.api import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls))
]
