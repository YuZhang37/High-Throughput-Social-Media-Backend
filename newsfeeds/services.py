from gatekeeper.gate_keeper import GateKeeper
from gatekeeper.service_names import SWITCH_NEWSFEED_TO_HBASE
from newsfeeds.models import NewsFeed, HBaseNewsfeed
from twitter.cache import USER_NEWSFEED_LIST_PATTERN
from utils.redisUtils.redis_serializers import RedisHBaseSerializer, RedisModelSerializer
from utils.redisUtils.redis_services import RedisService


class NewsFeedService:

    @classmethod
    def _lazy_load_newsfeeds(cls, user_id):
        def _lazy_newsfeeds(size):
            if GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
                newsfeeds = HBaseNewsfeed.filter(
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
            tweet_id=tweet.id, user_id=tweet.user_id, created_at=tweet.created_at
        )

    @classmethod
    def get_cached_newsfeed_list(cls, user_id):
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=user_id)
        get_newsfeeds = cls._lazy_load_newsfeeds(user_id=user_id)
        serializer = cls.get_serializer(SWITCH_NEWSFEED_TO_HBASE)
        newsfeed_list = RedisService.get_objects(
            key=key, get_objects=get_newsfeeds, serializer=serializer
        )
        return newsfeed_list

    @classmethod
    def push_newsfeed_to_cache(cls, obj: NewsFeed):
        get_objects = cls._lazy_load_newsfeeds(user_id=obj.user_id)
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=obj.user_id)
        serializer = cls.get_serializer(SWITCH_NEWSFEED_TO_HBASE)
        RedisService.push_object(
            key=key, obj=obj, get_objects=get_objects, serializer=serializer
        )

    @classmethod
    def create_newsfeed(cls, user_id, tweet_id, created_at):
        if not GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            newsfeed = NewsFeed.objects.create(user_id=user_id, tweet_id=tweet_id)
        else:
            newsfeed = HBaseNewsfeed.create(
                user_id=user_id, tweet_id=tweet_id, created_at=created_at
            )
        return newsfeed

    @classmethod
    def get_model_class(cls):
        if GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            return HBaseNewsfeed
        return NewsFeed

    @classmethod
    def batch_create_newsfeeds(cls, newsfeeds):
        if not GateKeeper.is_switch_on(SWITCH_NEWSFEED_TO_HBASE):
            NewsFeed.objects.bulk_create(newsfeeds)
        else:
            HBaseNewsfeed.batch_create(newsfeeds)
