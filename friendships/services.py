from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWING_PATTERN


cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService:

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship\
            .objects.filter(to_user=user)\
            .prefetch_related('from_user')
        followers = [
            friendship.from_user
            for friendship in friendships
        ]
        return followers

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        value = cache.get(key)
        if value is not None:
            return value
        friendships = Friendship.objects.filter(from_user=from_user_id)
        following_user_id_set = set([
            # don't use friendship.to_user.id, N + 1 queries
            friendship.to_user_id for friendship in friendships
        ])
        cache.set(key, following_user_id_set)
        return following_user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        cache.delete(key)
