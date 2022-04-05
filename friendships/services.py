import time

from django.conf import settings
from django.core.cache import caches

from friendships.hbase_models import HBaseFollowing, HBaseFollower
from friendships.models import Friendship
from gatekeeper.gate_keeper import GateKeeper
from gatekeeper.service_names import SWITCH_FRIENDSHIP_TO_HBASE
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
    def get_followings_id_set(cls, from_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        value = cache.get(key)
        if value is not None:
            return value
        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            friendships = Friendship.objects.filter(from_user=from_user_id)
        else:
            friendships = HBaseFollowing.filter(
                prefix={'from_user_id': from_user_id}
            )
        followings_id_set = set([
            # don't use friendship.to_user.id, N + 1 queries
            friendship.to_user_id for friendship in friendships
        ])
        cache.set(key, followings_id_set)
        return followings_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        cache.delete(key)

    @classmethod
    def get_followers_id_list(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user=to_user_id)
        followers_id_list = [
            friendship.from_user_id for friendship in friendships
        ]
        return followers_id_list

    # no need to pass created_at, django ORM will automatically pick up the timestamp
    # when we set up auto-now-add=True
    @classmethod
    def follow(cls, from_user_id, to_user_id):
        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            friendship = Friendship.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )
            return friendship
        created_at = int(time.time() * 1000000)
        HBaseFollowing.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=created_at
        )
        friendship = HBaseFollower.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=created_at
        )
        return friendship
