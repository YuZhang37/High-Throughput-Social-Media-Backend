from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_main_task
from twitter.cache import USER_NEWSFEED_LIST_PATTERN
from utils.redisUtils.redis_services import RedisService


class NewsFeedService:

    @classmethod
    def fan_out_to_followers(cls, tweet):
        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id)

    @classmethod
    def get_cached_newsfeed_list(cls, user_id, queryset=None):
        if not queryset:
            queryset = NewsFeed.objects.filter(user_id=user_id)\
                .order_by('-created_at')
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=user_id)
        newsfeed_list = RedisService.get_objects(key, queryset)
        return newsfeed_list

    @classmethod
    def push_newsfeed_to_cache(cls, obj: NewsFeed):
        queryset = NewsFeed.objects.filter(user_id=obj.user_id).order_by('-created_at')
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=obj.user_id)
        RedisService.push_object(key, obj, queryset)
