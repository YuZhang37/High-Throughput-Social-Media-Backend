from newsfeeds.models import NewsFeed
from testing.testcases import TestCase


class TestNewsFeedModel(TestCase):

    def test_newsfeed_model(self):
        user1 = self.create_user('user1')
        tweet = self.create_tweet(user1)
        newsfeed = NewsFeed.objects.create(user=user1, tweet=tweet)
        self.assertNotEqual(newsfeed, None)
        self.assertEqual(newsfeed.user, user1)
        self.assertEqual(newsfeed.tweet, tweet)
