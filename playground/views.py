from django.shortcuts import render
from rest_framework import viewsets

from core.models import UserProfile
from likes.models import Like


def calculate():
    x = 1
    y = 2
    return x + y


def say_hello(request):
    profile = UserProfile.objects.filter(id=3).first()
    url = profile.avatar.url
    print(url)
    # like = Like.objects.all().first()
    # model_name = like.content_type.model
    # print(model_name)
    # print(model_name == 'comment')
    # print(model_name == 'tweet')
    return render(request, 'playground/hello.html', {'name': 'Marvin', 'value': url})


class PlayViewSet(viewsets.ModelViewSet):
    pass
