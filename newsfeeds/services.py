from django.conf import settings

from gatekeeper.gate_keeper import GateKeeper
from gatekeeper.service_names import SWITCH_NEWSFEED_TO_HBASE
from newsfeeds.models import NewsFeed, HBaseNewsFeed
from twitter.cache import USER_NEWSFEED_LIST_PATTERN
from utils.redisUtils.redis_serializers import RedisHBaseSerializer, RedisModelSerializer
from utils.redisUtils.redis_services import RedisService


class NewsFeedService:

    @classmethod
    def _lazy_load_newsfeeds(cls, user_id):
        def _lazy_newsfeeds(size):
            if GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
                newsfeeds = HBaseNewsFeed.filter(
                    prefix={'user_id': user_id}, limit=size, reverse=True
                )
                return newsfeeds
            else:
                queryset = NewsFeed.objects.filter(user_id=user_id)\
                    .order_by('-created_at')[:size]
                return queryset
        return _lazy_newsfeeds

    @classmethod
    def get_serializer(cls, gk_name):
        if GateKeeper.is_switch_on(gk_name):
            serializer = RedisHBaseSerializer
        else:
            serializer = RedisModelSerializer
        return serializer

    @classmethod
    def fan_out_to_followers(cls, tweet):
        from newsfeeds.tasks import fanout_newsfeeds_main_task
        fanout_newsfeeds_main_task.delay(
            tweet_id=tweet.id, user_id=tweet.user_id, created_at=tweet.timestamp
        )

    @classmethod
    def get_cached_newsfeed_list(cls, user_id):
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=user_id)
        lazy_get_newsfeeds = cls._lazy_load_newsfeeds(user_id=user_id)
        serializer = cls.get_serializer(SWITCH_NEWSFEED_TO_HBASE)
        result = lazy_get_newsfeeds(size=settings.REDIS_CACHED_LIST_LIMIT_LENGTH)
        newsfeed_list = RedisService.get_objects(
            key=key, lazy_get_objects=lazy_get_newsfeeds, serializer=serializer
        )
        return newsfeed_list

    @classmethod
    def push_newsfeed_to_cache(cls, obj: NewsFeed):
        lazy_get_objects = cls._lazy_load_newsfeeds(user_id=obj.user_id)
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=obj.user_id)
        serializer = cls.get_serializer(SWITCH_NEWSFEED_TO_HBASE)
        RedisService.push_object(
            key=key, obj=obj, lazy_get_objects=lazy_get_objects, serializer=serializer
        )

    @classmethod
    def create_newsfeed(cls, user_id, tweet_id, created_at):
        if not GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            newsfeed = NewsFeed.objects.create(user_id=user_id, tweet_id=tweet_id)
        else:
            newsfeed = HBaseNewsFeed.create(
                user_id=user_id, tweet_id=tweet_id, created_at=created_at
            )
            cls.push_newsfeed_to_cache(newsfeed)
        return newsfeed

    @classmethod
    def get_model_class(cls):
        if GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            return HBaseNewsFeed
        return NewsFeed

    @classmethod
    def batch_create_newsfeeds(cls, newsfeeds):
        if not GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            NewsFeed.objects.bulk_create(newsfeeds)
        else:
            HBaseNewsFeed.batch_create(newsfeeds)
        for newsfeed in newsfeeds:
            NewsFeedService.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_newsfeed(cls, user_id=None):
        if GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            if user_id:
                newsfeeds = HBaseNewsFeed.filter(
                    prefix={'user_id': user_id}, reverse=True
                )
            else:
                newsfeeds = HBaseNewsFeed.filter(reverse=True)
        else:
            if user_id:
                newsfeeds = NewsFeed.objects.filter(user_id=user_id)\
                    .order_by('-created_at')
            else:
                newsfeeds = NewsFeed.objects.all().order_by('-created_at')
        return newsfeeds

    @classmethod
    def get_newsfeed_count(cls, user_id=None):
        newsfeeds = cls.get_newsfeed(user_id=user_id)
        return len(newsfeeds)
