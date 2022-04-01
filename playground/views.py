import logging
import time

import happybase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import render
from rest_framework import viewsets

from core import models
from core.models import User
from friendships.hbase_models import HBaseFollower, HBaseFollowing
from tweets.models import Tweet
from twitter.cache import OBJECT_PATTERN
from twitter.celery import debug_task


def calculate():
    x = 1
    y = 2
    return x + y


def say_hello(request):
    conn = happybase.Connection()
    table = conn.table('friendship_followers')
    # rows = table.scan(
    #     row_start='20000000000000000000:1648829427289107',
    #     row_stop='02000000000000000000:1648818414519579',
    #     reverse=True,
    # )
    rows = table.scan(
        # row_start='20000000000000000000:1648829427289107',
        # row_stop='02000000000000000000:1648818414519579',
        # row_prefix=b'20',
        reverse=True,
    )
    print(rows)
    for row in rows:
        print(row)

    # HBaseFollower.create_table()
    # HBaseFollowing.create_table()

    # print('first test:')
    # t = time.time()
    # t = int(t * 1000000)
    # print(f'from_user_id: 1, to_user_id:2, created_at: {t}')
    # HBaseFollower.create(from_user_id=1, to_user_id=2, created_at=t)
    # row = HBaseFollower.get(to_user_id=2, created_at=t)
    # print(row)
    # time.sleep(2)
    #
    # print('second test:')
    # t2 = time.time()
    # t2 = int(t2 * 1000000)
    # print(f'from_user_id: 10, to_user_id:20, created_at: {t2}')
    # hbase_follower = HBaseFollower(from_user_id=10, to_user_id=20, created_at=t2)
    # hbase_follower.save()
    # row = HBaseFollower.get(to_user_id=20, created_at=t2)
    # print(row)
    #
    # print('third test:')
    # t3 = time.time()
    # t3 = int(t3 * 1000000)
    # print(f'from_user_id: 1, to_user_id:2, created_at: {t3}')
    # HBaseFollowing.create(from_user_id=1, to_user_id=2, created_at=t3)
    # row = HBaseFollowing.get(from_user_id=1, created_at=t3)
    # print(row)
    # time.sleep(2)
    #
    # print('forth test:')
    # t4 = time.time()
    # t4 = int(t4 * 1000000)
    # print(f'from_user_id: 10, to_user_id:20, created_at: {t4}')
    # hbase_following = HBaseFollowing(from_user_id=10, to_user_id=20, created_at=t2)
    # hbase_following.save()
    # row = HBaseFollowing.get(from_user_id=10, created_at=t2)
    # print(row)

    # debug_task.delay()

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
