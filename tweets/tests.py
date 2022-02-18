from django.contrib.auth import get_user_model
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hours_to_now(self):
        user1 = get_user_model().objects.create_user(username='user1')
        tweet = Tweet.objects.create(user=user1, content='hello world')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
