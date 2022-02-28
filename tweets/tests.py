from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
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

