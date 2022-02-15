from django.urls import path

from playground import views

# url config
urlpatterns = [
    path('hello/', views.say_hello),
]
