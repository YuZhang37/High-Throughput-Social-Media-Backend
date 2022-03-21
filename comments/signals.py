from utils.redisUtils.redis_services import RedisService


def incr_comments_count(sender, instance, created, **kwargs):
    if not created:
        return
    from django.db.models import F
    from tweets.models import Tweet
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') + 1
    )
    RedisService.incr_count_key(instance.tweet, 'comments_count')


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') - 1
    )
    RedisService.decr_count_key(instance.tweet, 'comments_count')

