from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from twitter.cache import LIKED_OBJECT_PATTERN
from utils.redisUtils.redis_serializers import IntegerSerializer
from utils.redisUtils.redis_services import RedisService


class LikeService:

    @classmethod
    def _lazy_load_liked_objects(cls, user_id, model_class):
        def _lazy_liked_objects():
            content_type = ContentType.objects.get_for_model(model_class)
            objects_likes = Like.objects.filter(
                user=user_id,
                content_type=content_type,
            ).order_by('-created_at')
            liked_objects_id = [
                object_like.object_id for object_like in objects_likes
            ]
            return liked_objects_id
        return _lazy_liked_objects

    @classmethod
    def get_liked_objects_id_set(cls, user_id, model_class):
        key = LIKED_OBJECT_PATTERN.format(
            class_name=model_class.__name__, user_id=user_id
        )
        lazy_get_objects = cls._lazy_load_liked_objects(
            user_id=user_id, model_class=model_class
        )
        liked_tweets_id = RedisService.get_from_set(
            key=key, lazy_get_objects=lazy_get_objects, serializer=IntegerSerializer
        )
        return liked_tweets_id

    @classmethod
    def add_liked_object_id_to_redis(cls, user_id, object_id, model_class):
        key = LIKED_OBJECT_PATTERN.format(
            class_name=model_class.__name__, user_id=user_id
        )
        lazy_get_objects = cls._lazy_load_liked_objects(
            user_id=user_id, model_class=model_class
        )
        RedisService.add_to_set(
            key=key,
            value=object_id,
            lazy_get_objects=lazy_get_objects,
            serializer=IntegerSerializer
        )

    @classmethod
    def remove_liked_object_id_from_redis(cls, user_id, object_id, model_class):
        key = LIKED_OBJECT_PATTERN.format(
            class_name=model_class.__name__, user_id=user_id
        )
        lazy_get_objects = cls._lazy_load_liked_objects(
            user_id=user_id, model_class=model_class
        )
        RedisService.remove_from_set(
            key=key,
            value=object_id,
            lazy_get_objects=lazy_get_objects,
            serializer=IntegerSerializer
        )


