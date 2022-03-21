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

