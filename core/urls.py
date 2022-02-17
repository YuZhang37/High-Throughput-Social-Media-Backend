from django.urls import path, include
from rest_framework import routers

from core.api import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('accounts', views.AccountViewSet, basename='account')
urlpatterns = [
    path('', include(router.urls))
]
