from django.contrib.contenttypes.models import ContentType

from core.models import User
from likes.models import Like
from tweets.models import Tweet


class LikeService:

    @classmethod
    def has_liked(cls, user, obj):
        if user.is_anonymous:
            return False
        content_type = ContentType.objects.get_for_model(obj.__class__)
        liked = Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=obj.id,
        ).exists()
        return liked
