from django.conf import settings
from django.db import models

from tweets.models import Tweet


class NewsFeed(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [['user', 'created_at', ], ]
        unique_together = [['user', 'tweet', ], ]
        ordering = ['user', '-created_at']

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'

