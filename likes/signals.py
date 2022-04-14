from utils.redisUtils.redis_services import RedisService


def incr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    model = instance.content_type.model_class()
    model.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') + 1
    )
    RedisService.incr_count_key(instance.content_object, 'likes_count')


def decr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    model = instance.content_type.model_class()
    model.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') - 1
    )
    RedisService.decr_count_key(instance.content_object, 'likes_count')


def add_liked_object_id_to_set(sender, instance, **kwargs):
    from likes.services import LikeService
    LikeService.add_liked_object_id_to_redis(
        user_id=instance.user_id,
        object_id=instance.object_id,
        model_class=instance.content_type.model_class()
    )


def remove_liked_object_id_from_set(sender, instance, **kwargs):
    from likes.services import LikeService
    LikeService.remove_liked_object_id_from_redis(
        user_id=instance.user_id,
        object_id=instance.object_id,
        model_class=instance.content_type.model_class()
    )

