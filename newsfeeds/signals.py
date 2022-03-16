
def push_newsfeed_to_cache_after_creation(sender, instance, created, **kwargs):
    if created:
        from newsfeeds.services import NewsfeedService
        NewsfeedService.push_newsfeed_to_cache(instance)
