from django.contrib.auth import get_user_model

from testing.testcases import TestCase
from tweets.models import Tweet
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
