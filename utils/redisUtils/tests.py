from testing.testcases import TestCase
from utils.redisUtils.redis_client import RedisClient


class UtilsTests(TestCase):

    def setUp(self):
        super(UtilsTests, self).setUp()
        RedisClient.clear_db()

    def test_connection(self):
        conn = RedisClient.get_connection()
        conn.lpush('redis_key', 1)
        conn.lpush('redis_key', 2)
        cached_list = conn.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [b'2', b'1'])

        RedisClient.clear_db()
        cached_list = conn.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [])
        