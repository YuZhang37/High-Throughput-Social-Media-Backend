from django.core.files.uploadedfile import SimpleUploadedFile

from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
from datetime import timedelta

from tweets.services import TweetService
from twitter.cache import USER_TWEET_LIST_PATTERN
from utils.redisUtils.redis_client import RedisClient
from utils.redisUtils.redis_serializers import RedisModelSerializer
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')
        self.tweet = self.create_tweet(self.user1)

    def test_hours_to_now(self):
        tweet = Tweet.objects.create(user=self.user1)
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        # 测试可以成功创建 photo 的数据对象
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.tweet.user,
            file=SimpleUploadedFile(
                name='my-photo.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        )
        # print("user:", photo.user)
        self.assertEqual(photo.user, self.user1)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        # self.assertEqual(photo.file, "")
        self.assertNotEqual(photo.file, "")
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)
        # print("photo:", photo)

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.user1)
        redis_client = RedisClient.get_redis_client()
        serialized_data = RedisModelSerializer.serialize(tweet)
        redis_client.set(f'tweet:{tweet.id}', serialized_data)
        data = redis_client.get(f'tweet:not_exists')
        self.assertEqual(data, None)

        data = redis_client.get(f'tweet:{tweet.id}')
        cached_tweet = RedisModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)


class TweetServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')

    def test_get_user_tweets(self):
        tweet_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.user1, 'tweet {}'.format(i))
            tweet_ids.append(tweet.id)
        tweet_ids = tweet_ids[::-1]

        RedisClient.clear_db()

        # cache miss
        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([t.id for t in tweets], tweet_ids)

        # cache hit
        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([t.id for t in tweets], tweet_ids)

        # cache updated
        new_tweet = self.create_tweet(self.user1, 'new tweet')
        tweets = TweetService.get_cached_tweets(self.user1.id)
        tweet_ids.insert(0, new_tweet.id)
        self.assertEqual([t.id for t in tweets], tweet_ids)

    def test_create_new_tweet_before_get_cached_tweets(self):
        tweet1 = self.create_tweet(self.user1, 'tweet1')

        RedisClient.clear_db()
        redis_client = RedisClient.get_redis_client()

        key = USER_TWEET_LIST_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(redis_client.exists(key), False)
        tweet2 = self.create_tweet(self.user1, 'tweet2')
        self.assertEqual(redis_client.exists(key), True)

        tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([t.id for t in tweets], [tweet2.id, tweet1.id])
