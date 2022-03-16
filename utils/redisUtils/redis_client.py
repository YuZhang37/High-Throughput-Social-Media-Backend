import redis
from django.conf import settings


class RedisClient:
    redis_client = None

    @classmethod
    def get_redis_client(cls):
        if cls.redis_client:
            return cls.redis_client
        cls.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.redis_client

    @classmethod
    def clear_db(cls):
        if not settings.TESTING:
            raise Exception('You can not clear redis in production')
        redis_client = cls.get_redis_client()
        redis_client.flushdb()

