from utils.memcached_services import MemcachedService


def incr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet
    model = instance.content_type.model_class()
    model.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') + 1
    )
    if model == Tweet:
        MemcachedService.invalidate_object(Tweet, instance.object_id)


def decr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet
    model = instance.content_type.model_class()
    model.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') - 1
    )
    if model == Tweet:
        MemcachedService.invalidate_object(Tweet, instance.object_id)
