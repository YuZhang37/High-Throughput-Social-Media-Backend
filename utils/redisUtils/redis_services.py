from django.conf import settings

from utils.redisUtils.redis_client import RedisClient
from utils.redisUtils.redis_serializers import RedisModelSerializer


class RedisService:

    @classmethod
    def _load_objects(cls, key, queryset):
        serialized_objects = []
        limited_queryset = list(queryset[:settings.REDIS_CACHED_LIST_LIMIT_LENGTH])
        for obj in limited_queryset:
            serialized_obj = RedisModelSerializer.serialize(obj)
            serialized_objects.append(serialized_obj)
        if serialized_objects:
            redis_client = RedisClient.get_redis_client()
            redis_client.rpush(key, *serialized_objects)
            redis_client.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return limited_queryset

    @classmethod
    def get_objects(cls, key, queryset):
        redis_client = RedisClient.get_redis_client()
        if not redis_client.exists(key):
            deserialized_objects = cls._load_objects(key, queryset)
            return deserialized_objects
        objects = redis_client.lrange(key, 0, -1)
        deserialized_objects = []
        for obj in objects:
            deserialized_object = RedisModelSerializer.deserialize(obj)
            deserialized_objects.append(deserialized_object)
        return deserialized_objects

    @classmethod
    def push_object(cls, key, obj, queryset):
        redis_client = RedisClient.get_redis_client()
        serialized_obj = RedisModelSerializer.serialize(obj)
        if not redis_client.exists(key):
            cls._load_objects(key, queryset)
            return
        redis_client.lpush(key, serialized_obj)
        redis_client.ltrim(key, 0, settings.REDIS_CACHED_LIST_LIMIT_LENGTH - 1)

    @classmethod
    def _get_count_key(cls, instance, attr):
        key = f'{instance.__class__.__name__}.{attr}:{instance.id}'
        return key

    @classmethod
    def incr_count_key(cls, instance, attr):
        if instance is None:
            return -1
        key = cls._get_count_key(instance, attr)
        redis_client = RedisClient.get_redis_client()
        if redis_client.exists(key):
            return redis_client.incr(key)

        count = getattr(instance, attr)
        redis_client.set(key, count, ex=settings.REDIS_KEY_EXPIRE_TIME)
        return count

    @classmethod
    def decr_count_key(cls, instance, attr):
        if instance is None:
            return -1
        key = cls._get_count_key(instance, attr)
        redis_client = RedisClient.get_redis_client()
        if redis_client.exists(key):
            return redis_client.decr(key)

        count = getattr(instance, attr)
        redis_client.set(key, count, ex=settings.REDIS_KEY_EXPIRE_TIME)
        return count

    @classmethod
    def get_count(cls, instance, attr):
        if instance is None:
            return -1
        key = cls._get_count_key(instance, attr)
        redis_client = RedisClient.get_redis_client()
        count = redis_client.get(key)
        if count is not None:
            return int(count)
        count = getattr(instance, attr)
        redis_client.set(key, count, ex=settings.REDIS_KEY_EXPIRE_TIME)
        return count











