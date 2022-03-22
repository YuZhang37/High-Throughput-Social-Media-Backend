from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.constants import NEWSFEED_FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, followers_id_list):
    from newsfeeds.services import NewsFeedService
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in followers_id_list
    ]
    NewsFeed.objects.bulk_create(newsfeeds)
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
    return '{} newsfeeds are created.'.format(len(followers_id_list))


@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, user_id):
    NewsFeed.objects.create(user_id=user_id, tweet_id=tweet_id)
    followers_id_list = FriendshipService.get_followers_id_list(user_id)
    index = 0
    size = len(followers_id_list)
    while index < size:
        followers_id_batch = followers_id_list[index: index + NEWSFEED_FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, followers_id_batch)
        index = index + NEWSFEED_FANOUT_BATCH_SIZE
    return '{} newsfeeds going to fanout, {} batch tasks are created.'.format(
        size, (size - 1) // NEWSFEED_FANOUT_BATCH_SIZE + 1
    )
