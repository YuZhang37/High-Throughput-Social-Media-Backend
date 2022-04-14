from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from tweets.models import Tweet
from twitter.cache import LIKED_TWEET_PATTERN
from utils.redisUtils.redis_serializers import IntegerSerializer
from utils.redisUtils.redis_services import RedisService


class LikeService:

    @classmethod
    def _lazy_load_liked_tweets(cls, user_id):
        def _lazy_liked_tweets():
            content_type = ContentType.objects.get_for_model(Tweet)
            tweets_likes = Like.objects.filter(
                user=user_id,
                content_type=content_type,
            ).order_by('-created_at')
            liked_tweets_id = [
                tweet_like.object_id for tweet_like in tweets_likes
            ]
            return liked_tweets_id
        return _lazy_liked_tweets

    @classmethod
    def get_liked_tweets_id_set(cls, user_id):
        key = LIKED_TWEET_PATTERN.format(user_id=user_id)
        lazy_get_objects = cls._lazy_load_liked_tweets(user_id=user_id)
        liked_tweets_id = RedisService.get_from_set(
            key=key, lazy_get_objects=lazy_get_objects, serializer=IntegerSerializer
        )
        return liked_tweets_id

    @classmethod
    def add_liked_tweet_id_to_redis(cls, user_id, tweet_id):
        key = LIKED_TWEET_PATTERN.format(user_id=user_id)
        lazy_get_objects = cls._lazy_load_liked_tweets(user_id)
        RedisService.add_to_set(
            key=key,
            value=tweet_id,
            lazy_get_objects=lazy_get_objects,
            serializer=IntegerSerializer
        )

    @classmethod
    def remove_liked_tweet_id_from_redis(cls, user_id, tweet_id):
        key = LIKED_TWEET_PATTERN.format(user_id=user_id)
        lazy_get_objects = cls._lazy_load_liked_tweets(user_id)
        RedisService.remove_from_set(
            key=key,
            value=tweet_id,
            lazy_get_objects=lazy_get_objects,
            serializer=IntegerSerializer
        )

    @classmethod
    def has_liked(cls, user, obj):
        if user.is_anonymous:
            return False
        content_type = ContentType.objects.get_for_model(obj.__class__)
        liked = Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=obj.id,
        ).exists()
        return liked

