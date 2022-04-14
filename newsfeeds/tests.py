
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEED_LIST_PATTERN
from utils.redisUtils.redis_client import RedisClient


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        super(NewsFeedServiceTests, self).setUp()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_get_cached_newsfeed_list(self):
        newsfeed_created_ats = []
        for i in range(3):
            tweet = self.create_tweet(self.user2)
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeed_created_ats.append(newsfeed.created_at)
        newsfeed_created_ats = newsfeed_created_ats[::-1]

        self.clear_cache()
        conn = RedisClient.get_connection()
        
        # cache miss
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key), False)
        newsfeeds = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        created_ats = [f.created_at for f in newsfeeds]
        self.assertEqual(created_ats, newsfeed_created_ats)

        # cache hit
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key), True)
        newsfeeds = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        created_ats = [f.created_at for f in newsfeeds]
        self.assertEqual(created_ats, newsfeed_created_ats)

    def test_push_newsfeed_to_cache(self):
        newsfeed_created_ats = []
        for i in range(3):
            tweet = self.create_tweet(self.user2)
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeed_created_ats.append(newsfeed.created_at)
        newsfeed_created_ats = newsfeed_created_ats[::-1]

        self.clear_cache()
        conn = RedisClient.get_connection()
        key = USER_NEWSFEED_LIST_PATTERN.format(user_id=self.user1.id)

        # cache miss, create new a newsfeed
        self.assertEqual(conn.exists(key), False)
        tweet = self.create_tweet(self.user1)
        new_newsfeed1 = self.create_newsfeed(self.user1, tweet)
        self.assertEqual(conn.exists(key), True)
        newsfeeds = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        newsfeed_created_ats.insert(0, new_newsfeed1.created_at)
        self.assertEqual([f.created_at for f in newsfeeds], newsfeed_created_ats)

        # cache hit, create another new newsfeed
        tweet = self.create_tweet(self.user1)
        new_newsfeed2 = self.create_newsfeed(self.user1, tweet)
        self.assertEqual(conn.exists(key), True)
        newsfeeds = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        newsfeed_created_ats.insert(0, new_newsfeed2.created_at)
        self.assertEqual([f.created_at for f in newsfeeds], newsfeed_created_ats)

    def test_newsfeeds_from_fan_out(self):
        self.user10 = self.create_user('user10')
        self.user11 = self.create_user('user11')
        self.user12 = self.create_user('user12')
        self.create_friendship(from_user=self.user10, to_user=self.user1)
        self.create_friendship(from_user=self.user11, to_user=self.user1)
        self.create_friendship(from_user=self.user12, to_user=self.user1)
        tweet1 = self.create_tweet(self.user1)
        tweet2 = self.create_tweet(self.user1)
        tweet_ids = [tweet2.id, tweet1.id]

        NewsFeedService.fan_out_to_followers(tweet1)
        NewsFeedService.fan_out_to_followers(tweet2)

        user1_newsfeeds = NewsFeedService.get_newsfeed(user_id=self.user1.id)
        self.assertEqual(
            [newsfeed.cached_tweet.id for newsfeed in user1_newsfeeds], tweet_ids
        )

        user11_newsfeeds = NewsFeedService.get_newsfeed(user_id=self.user11.id)
        self.assertEqual(
            [newsfeed.cached_tweet.id for newsfeed in user11_newsfeeds], tweet_ids
        )

    def test_newsfeeds_from_fan_out_with_cache(self):
        self.user10 = self.create_user('user10')
        self.user11 = self.create_user('user11')
        self.user12 = self.create_user('user12')
        self.create_friendship(from_user=self.user10, to_user=self.user1)
        self.create_friendship(from_user=self.user11, to_user=self.user1)
        self.create_friendship(from_user=self.user12, to_user=self.user1)
        tweet1 = self.create_tweet(self.user1)
        tweet2 = self.create_tweet(self.user1)
        tweet_ids = [tweet2.id, tweet1.id]

        NewsFeedService.fan_out_to_followers(tweet1)
        NewsFeedService.fan_out_to_followers(tweet2)

        conn = RedisClient.get_connection()

        key1 = USER_NEWSFEED_LIST_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key1), True)

        user1_newsfeeds = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        self.assertEqual(
            [newsfeed.cached_tweet.id for newsfeed in user1_newsfeeds], tweet_ids
        )

        key11 = USER_NEWSFEED_LIST_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key11), True)

        user11_newsfeeds = NewsFeedService.get_cached_newsfeed_list(self.user11.id)
        self.assertEqual(
            [newsfeed.cached_tweet.id for newsfeed in user11_newsfeeds], tweet_ids
        )


class NewsFeedTaskTests(TestCase):

    def setUp(self):
        super(NewsFeedTaskTests, self).setUp()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.user1, 'tweet 1')
        self.create_friendship(self.user2, self.user1)
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id, tweet.timestamp)
        self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batch tasks are created.')
        count = NewsFeedService.get_newsfeed_count()
        self.assertEqual(1 + 1, count)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        self.assertEqual(len(cached_list), 1)

        for i in range(2):
            user = self.create_user('someone_{}'.format(i))
            self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet 2')
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id, tweet.timestamp)
        self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batch tasks are created.')
        count = NewsFeedService.get_newsfeed_count()
        self.assertEqual(4 + 2, count)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        self.assertEqual(len(cached_list), 2)

        user = self.create_user('another user')
        self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet 3')
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id, tweet.timestamp)
        self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batch tasks are created.')
        count = NewsFeedService.get_newsfeed_count()
        self.assertEqual(8 + 3, count)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user2.id)
        self.assertEqual(len(cached_list), 3)

        for i in range(6):
            user = self.create_user('someone1_{}'.format(i))
            self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet 4')
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id, tweet.timestamp)
        self.assertEqual(msg, '10 newsfeeds going to fanout, 2 batch tasks are created.')
        count = NewsFeedService.get_newsfeed_count()
        self.assertEqual(18 + 4, count)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        self.assertEqual(len(cached_list), 4)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user2.id)
        self.assertEqual(len(cached_list), 4)

        user = self.create_user('another user 2')
        self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet 5')
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id, tweet.timestamp)
        self.assertEqual(msg, '11 newsfeeds going to fanout, 3 batch tasks are created.')
        count = NewsFeedService.get_newsfeed_count()
        self.assertEqual(29 + 5, count)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user1.id)
        self.assertEqual(len(cached_list), 5)
        cached_list = NewsFeedService.get_cached_newsfeed_list(self.user2.id)
        self.assertEqual(len(cached_list), 5)
