from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import render
from rest_framework import viewsets

from core import models
from core.models import User
from tweets.models import Tweet
from twitter.cache import OBJECT_PATTERN
from twitter.celery import debug_task


def calculate():
    x = 1
    y = 2
    return x + y


def say_hello(request):

    debug_task.delay()

    # print('get_user_model: ', get_user_model())
    # print('User', User)
    # print('Tweet', Tweet)
    #
    # print('User_name', User.__name__)
    # print('Tweet_name', Tweet.__name__)
    #
    # print('User_str', User.__str__)
    # print('Tweet_str', Tweet.__str__)
    # key = OBJECT_PATTERN.format(class_name=get_user_model(), object_id=3)
    # print('key', key)
    # key = USER_PATTERN.format(user_id=6)
    # cache.delete(key)
    # result = cache.get(key)
    # print('None: ', result)
    # user = models.User.objects.get(id=6)
    # cache.set(key, user)
    # result = cache.get(key)
    # print('exist: ', result)
    # user.username = 'testname66'
    # user.save()
    # result = cache.get(key)
    # print('None: ', result)
    # user = models.User.objects.get(id=6)
    # cache.set(key, user)
    # result = cache.get(key)
    # print('exist: ', result)

    # profile = UserProfile.objects.filter(id=3).first()
    # url = profile.avatar.url
    # print(url)
    # like = Like.objects.all().first()
    # model_name = like.content_type.model
    # print(model_name)
    # print(model_name == 'comment')
    # print(model_name == 'tweet')
    return render(request, 'playground/hello.html', {'name': 'Marvin', 'value': 'url'})


class PlayViewSet(viewsets.ModelViewSet):
    pass
