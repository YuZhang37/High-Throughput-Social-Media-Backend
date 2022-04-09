from django_hbase import models
from tweets.models import Tweet
from utils.memcached_services import MemcachedService


class HBaseNewsFeed(models.HBaseModel):
    user_id = models.IntegerField(reverse=True)
    tweet_id = models.IntegerField(column_family='cf')
    created_at = models.TimestampField()

    class Meta:
        table_name = 'newsfeeds'
        row_key = ('user_id', 'created_at')

    def __str__(self):
        return '{} inbox of {}: {}'.format(self.created_at, self.user_id, self.tweet_id)

    @property
    def cached_tweet(self):
        tweet = MemcachedService.get_object_from_cache(Tweet, self.tweet_id)
        return tweet
