from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient
from comments.models import Comment
from django_hbase.models import HBaseModel
from friendships.services import FriendshipService
from gatekeeper.gate_keeper import GateKeeper
from gatekeeper.service_names import SWITCH_FRIENDSHIP_TO_HBASE, SWITCH_NEWSFEED_TO_HBASE
from likes.models import Like
from newsfeeds.services import NewsFeedService
from tweets.models import Tweet
from utils.redisUtils.redis_client import RedisClient


class TestCase(DjangoTestCase):
    hbase_tables_created = False

    def setUp(self):
        self.clear_cache()
        try:
            self.hbase_tables_created = True
            for model_class in HBaseModel.__subclasses__():
                model_class.create_table()
        except Exception:
            self.tearDown()
            raise

    def tearDown(self):
        if not self.hbase_tables_created:
            return
        for model_class in HBaseModel.__subclasses__():
            model_class.drop_table()
        self.hbase_tables_created = False

    def clear_cache(self):
        caches['testing'].clear()
        RedisClient.clear_db()
        GateKeeper.turn_on(SWITCH_FRIENDSHIP_TO_HBASE)
        GateKeeper.turn_on(SWITCH_NEWSFEED_TO_HBASE)

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@mytwitter.com'
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return get_user_model().objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance
        # it works
        # instance2 = Like.objects.create(content_object=target, user=user)
        # return instance2

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_newsfeed(self, user, tweet):
        newsfeed = NewsFeedService.create_newsfeed(
            user_id=user.id, tweet_id=tweet.id, created_at=tweet.timestamp
        )
        return newsfeed

    def create_friendship(self, from_user, to_user):
        return FriendshipService.follow(
            from_user_id=from_user.id, to_user_id=to_user.id
        )
