from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete, post_save

from likes.models import Like
from tweets.constants import TWEET_PHOTO_DEFAULT_STATUS, TWEET_PHOTO_STATUS_CHOICES
from utils.memcached_services import MemcachedService
from utils.signals import invalidate_object_cache
from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        # here I don't set blank=true, since I don't want user to input blank,
        # null value is only set when the referred user is deleted
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [['user', 'created_at'], ]
        ordering = ['user', '-created_at']

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        content_type = ContentType.objects.get_for_model(Tweet)
        object_id = self.id
        likes = Like.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-created_at')
        return likes

    def __str__(self):
        return f'{self.user} {self.created_at} {self.content}'

    @property
    def cached_user(self):
        user = MemcachedService.get_object_from_cache(
            model_class=get_user_model(), object_id=self.user_id
        )
        return user


class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # redundant information, useful for querying related to users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    file = models.FileField(upload_to='tweetphotos/%Y/%m/%d/')
    status = models.IntegerField(
        default=TWEET_PHOTO_DEFAULT_STATUS,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )
    order = models.IntegerField(default=0)
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # The first three indices are mostly used by the ones
        # who checking the validation of user postings.
        index_together = [
            ['user', 'created_at'],
            ['status', 'created_at'],
            ['has_deleted', 'created_at'],
            ['tweet', 'order'],
        ]

    def __str__(self):
        return f'{self.user.id} - {self.tweet.id} - {self.file}'


pre_delete.connect(receiver=invalidate_object_cache, sender=Tweet)
post_save.connect(receiver=invalidate_object_cache, sender=Tweet)


