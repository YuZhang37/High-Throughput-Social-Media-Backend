from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedServices:

    @classmethod
    def fan_out_to_followers(cls, tweet):
        user = tweet.user
        followers = FriendshipService.get_followers(user)
        followers.append(user)
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in followers
        ]

        NewsFeed.objects.bulk_create(newsfeeds)
