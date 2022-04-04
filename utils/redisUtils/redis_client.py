import redis
from django.conf import settings


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        if cls.conn:
            return cls.conn
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear_db(cls):
        if not settings.TESTING:
            raise Exception('You can not clear redis in production')
        conn = cls.get_connection()
        conn.flushdb()

