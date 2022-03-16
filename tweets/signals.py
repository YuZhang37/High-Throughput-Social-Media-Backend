

def push_tweet_to_cache_after_creation(sender, instance, created, **kwargs):
    if created:
        from tweets.services import TweetService
        TweetService.push_tweet_to_cache(instance)
