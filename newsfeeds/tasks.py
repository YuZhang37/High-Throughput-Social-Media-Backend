from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.constants import NEWSFEED_FANOUT_BATCH_SIZE, NEWSFEED_FANOUT_BATCH_NUM_LIMIT
from newsfeeds.services import NewsFeedService
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='newsfeeds', exchange='celery', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, total_followers_id_list, created_at):
    from newsfeeds.services import NewsFeedService
    model_class = NewsFeedService.get_model_class()
    current_followers_id_list = total_followers_id_list[:NEWSFEED_FANOUT_BATCH_SIZE]
    next_followers_id_list = total_followers_id_list[NEWSFEED_FANOUT_BATCH_SIZE:]
    newsfeeds = [
        model_class(
            user_id=follower_id, tweet_id=tweet_id, created_at=created_at
        )
        for follower_id in current_followers_id_list
    ]
    NewsFeedService.batch_create_newsfeeds(newsfeeds)
    if next_followers_id_list:
        fanout_newsfeeds_batch_task.delay(tweet_id, next_followers_id_list, created_at)
    return '{} newsfeeds are created. {} newsfeeds are going to fanout in next batch'\
        .format(len(current_followers_id_list), len(next_followers_id_list))


@shared_task(routing_key='default', exchange='celery', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, user_id, created_at):
    NewsFeedService.create_newsfeed(
        user_id=user_id, tweet_id=tweet_id, created_at=created_at
    )
    followers_id_list = FriendshipService.get_followers_id_list(user_id)
    index = 0
    size = len(followers_id_list)
    batch_size = NEWSFEED_FANOUT_BATCH_SIZE
    if size / NEWSFEED_FANOUT_BATCH_SIZE > NEWSFEED_FANOUT_BATCH_NUM_LIMIT:
        batch_size = size // (NEWSFEED_FANOUT_BATCH_SIZE - 1)

    while index < size:
        followers_id_batch = followers_id_list[index: index + batch_size]
        fanout_newsfeeds_batch_task.delay(tweet_id, followers_id_batch, created_at)
        index = index + batch_size
    return '{} newsfeeds going to fanout, {} batch tasks are created.'.format(
        size, (size - 1) // batch_size + 1
    )
