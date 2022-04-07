from django.conf import settings
from django.db import models
from tweets.constants import TWEET_PHOTO_DEFAULT_STATUS, TWEET_PHOTO_STATUS_CHOICES
from .tweet import Tweet


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
