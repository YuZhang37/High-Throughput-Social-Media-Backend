from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.constants import NEWSFEED_FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, followers_id_list, created_at):
    from newsfeeds.services import NewsFeedService
    newsfeeds = [
        NewsFeedService.create_newsfeed(
            user_id=follower_id, tweet_id=tweet_id, created_at=created_at
        )
        for follower_id in followers_id_list
    ]
    NewsFeedService.batch_create_newsfeeds(newsfeeds)
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
    return '{} newsfeeds are created.'.format(len(followers_id_list))


@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, user_id, created_at):
    NewsFeedService.create_newsfeed(
        user_id=user_id, tweet_id=tweet_id, created_at=created_at
    )
    followers_id_list = FriendshipService.get_followers_id_list(user_id)
    index = 0
    size = len(followers_id_list)
    while index < size:
        followers_id_batch = followers_id_list[index: index + NEWSFEED_FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, followers_id_batch, created_at)
        index = index + NEWSFEED_FANOUT_BATCH_SIZE
    return '{} newsfeeds going to fanout, {} batch tasks are created.'.format(
        size, (size - 1) // NEWSFEED_FANOUT_BATCH_SIZE + 1
    )
