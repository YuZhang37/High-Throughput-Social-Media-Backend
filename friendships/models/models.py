from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, pre_delete

from friendships.signals import friendship_changed
from utils.memcached_services import MemcachedService


class Friendship(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='from_user_set'
    )

    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='to_user_set'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [
            ['from_user', 'created_at'],
            ['to_user', 'created_at'],
        ]
        unique_together = [
            ['from_user', 'to_user']
        ]
        # ordering = ['-created_at']

    def __str__(self):
        return f'{self.from_user} follows {self.to_user}'


post_save.connect(friendship_changed, sender=Friendship)
pre_delete.connect(friendship_changed, sender=Friendship)