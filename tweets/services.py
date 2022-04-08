from tweets.models import TweetPhoto, Tweet
from twitter.cache import USER_TWEET_LIST_PATTERN
from utils.redisUtils.redis_serializers import RedisModelSerializer
from utils.redisUtils.redis_services import RedisService


class TweetPhotoService:

    @classmethod
    def create_tweet_photos(cls, tweet, files):
        tweet_photos = []
        for index, file in enumerate(files):
            instance = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                order=index,
                file=file,
            )
            tweet_photos.append(instance)
        TweetPhoto.objects.bulk_create(tweet_photos)


class TweetService:

    @classmethod
    def _lazy_load_tweets(cls, user_id):
        def _lazy_tweets(size):
            queryset = Tweet.objects.filter(user_id=user_id) \
                           .order_by('-created_at')[:size]
            return queryset
        return _lazy_tweets

    @classmethod
    def get_cached_tweets(cls, user_id, queryset=None):
        get_tweets = cls._lazy_load_tweets(user_id=user_id)
        key = USER_TWEET_LIST_PATTERN.format(user_id=user_id)
        tweets = RedisService.get_objects(
            key=key, get_objects=get_tweets
        )
        return tweets

    @classmethod
    def push_tweet_to_cache(cls, tweet):
        key = USER_TWEET_LIST_PATTERN.format(user_id=tweet.user_id)
        get_tweets = cls._lazy_load_tweets(user_id=tweet.user_id)
        RedisService.push_object(
            key=key, obj=tweet, get_objects=get_tweets,
        )
