import redis
from django.conf import settings


class RedisClient:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance
        cls.instance = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.instance

    @classmethod
    def clear_db(cls):
        if not settings.TESTING:
            raise Exception('You can not clear redis in production')
        instance = cls.get_instance()
        instance.flushdb()

