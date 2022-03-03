from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models

from likes.models import Like
from tweets.models import Tweet
from utils.memcached_services import MemcachedService


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [['tweet', 'created_at', ], ]

    @property
    def like_set(self):
        content_type = ContentType.objects.get_for_model(Comment)
        object_id = self.id
        likes = Like.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-created_at')
        return likes

    @property
    def cached_user(self):
        user = MemcachedService.get_object_from_cache(
            model_class=get_user_model(), object_id=self.user_id
        )
        return user

    def __str__(self):
        return f'{self.created_at} - {self.user} ' \
               f'comments on {self.tweet}: {self.content}'



