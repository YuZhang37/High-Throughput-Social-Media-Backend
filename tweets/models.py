from django.conf import settings
from django.db import models

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

    def __str__(self):
        return f'{self.user} {self.created_at} {self.content}'
