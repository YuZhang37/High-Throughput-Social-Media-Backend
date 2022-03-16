from testing.testcases import TestCase
from utils.redisUtils.redis_client import RedisClient


class UtilsTests(TestCase):

    def setUp(self):
        RedisClient.clear_db()

    def test_redis_client(self):
        redis_client = RedisClient.get_redis_client()
        redis_client.lpush('redis_key', 1)
        redis_client.lpush('redis_key', 2)
        cached_list = redis_client.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [b'2', b'1'])

        RedisClient.clear_db()
        cached_list = redis_client.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [])
        