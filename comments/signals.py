from utils.redisUtils.redis_services import RedisService


def incr_comments_count(sender, instance, created, **kwargs):
    if not created:
        return
    from django.db.models import F
    from tweets.models import Tweet
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') + 1
    )
    tweet = instance.tweet
    RedisService.incr_count_key(tweet, 'comments_count')


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') - 1
    )
    tweet = instance.tweet
    RedisService.decr_count_key(tweet, 'comments_count')

