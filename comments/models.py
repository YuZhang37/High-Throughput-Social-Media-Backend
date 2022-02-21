from django.conf import settings
from django.db import models

from tweets.models import Tweet


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

    def __str__(self):
        return f'{self.created_at} - {self.user} ' \
               f'comments on {self.tweet}: {self.content}'



