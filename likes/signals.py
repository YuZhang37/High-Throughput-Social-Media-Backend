
def incr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    model = instance.content_type.model_class()
    model.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') + 1
    )


def decr_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    model = instance.content_type.model_class()
    model.objects.filter(id=instance.object_id).update(
        likes_count=F('likes_count') - 1
    )

