from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fan_out_to_followers_task(tweet_id):
    from newsfeeds.services import NewsFeedService
    tweet = Tweet.objects.get(id=tweet_id)
    user = tweet.user
    followers = FriendshipService.get_followers(user)
    followers.append(user)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in followers
    ]

    NewsFeed.objects.bulk_create(newsfeeds)

    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
