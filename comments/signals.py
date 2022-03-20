
def incr_comments_count(sender, instance, created, **kwargs):
    if not created:
        return
    from django.db.models import F
    from tweets.models import Tweet
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') + 1
    )


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') - 1
    )

