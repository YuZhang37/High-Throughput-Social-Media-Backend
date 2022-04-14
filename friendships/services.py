import time

from django.conf import settings
from django.core.cache import caches

from friendships.models import HBaseFollowing, HBaseFollower
from friendships.models import Friendship
from gatekeeper.gate_keeper import GateKeeper
from gatekeeper.service_names import SWITCH_FRIENDSHIP_TO_HBASE
from twitter.cache import FOLLOWING_PATTERN
from utils.redisUtils.redis_serializers import IntegerSerializer
from utils.redisUtils.redis_services import RedisService

cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService:

    @classmethod
    def _lazy_load_followings(cls, from_user_id):
        def _lazy_followings():
            if GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
                followings = HBaseFollowing.filter(
                    prefix={'from_user_id': from_user_id}, reverse=True
                )
            else:
                followings = Friendship.objects.filter(from_user_id=from_user_id) \
                               .order_by('-created_at')
            followings_id = [
                following.to_user_id for following in followings
            ]
            return followings_id
        return _lazy_followings

    @classmethod
    def get_followings_id_set(cls, from_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        lazy_get_objects = cls._lazy_load_followings(from_user_id)
        followings_id = RedisService.get_from_set(
            key=key, lazy_get_objects=lazy_get_objects, serializer=IntegerSerializer
        )
        return followings_id

    @classmethod
    def get_followers_id_list(cls, to_user_id):
        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            friendships = Friendship.objects.filter(to_user=to_user_id)
        else:
            prefix = {'to_user_id': to_user_id}
            friendships = HBaseFollower.filter(prefix=prefix)
        followers_id_list = [
            friendship.from_user_id for friendship in friendships
        ]
        return followers_id_list

    @classmethod
    def add_following_id_to_redis(cls, from_user_id, to_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        lazy_get_objects = cls._lazy_load_followings(from_user_id)
        RedisService.add_to_set(
            key=key,
            value=to_user_id,
            lazy_get_objects=lazy_get_objects,
            serializer=IntegerSerializer
        )

    @classmethod
    def remove_following_id_from_redis(cls, from_user_id, to_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        lazy_get_objects = cls._lazy_load_followings(from_user_id)
        RedisService.remove_from_set(
            key=key,
            value=to_user_id,
            lazy_get_objects=lazy_get_objects,
            serializer=IntegerSerializer
        )

    # no need to pass created_at, django ORM will automatically pick up the timestamp
    # when we set up auto-now-add=True
    @classmethod
    def follow(cls, from_user_id, to_user_id):
        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            friendship = Friendship.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )
        else:
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
        cls.add_following_id_to_redis(
            from_user_id=friendship.from_user_id,
            to_user_id=friendship.to_user_id
        )
        return friendship

    @classmethod
    def unfollow(cls, from_user_id, to_user_id):
        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            deleted, _ = Friendship.objects.filter(
                from_user=from_user_id,
                to_user=to_user_id,
            ).delete()
            result = deleted
        else:
            instance = cls.get_following_instance(
                from_user_id=from_user_id, to_user_id=to_user_id
            )
            if instance is None:
                result = 0
            else:
                HBaseFollowing.delete(
                    from_user_id=from_user_id, created_at=instance.created_at
                )
                HBaseFollower.delete(
                    to_user_id=to_user_id, created_at=instance.created_at
                )
                result = 1
        cls.remove_following_id_from_redis(
            from_user_id=from_user_id, to_user_id=to_user_id
        )
        return result

    @classmethod
    def get_following_instance(cls, from_user_id, to_user_id):
        followings = HBaseFollowing.filter(
            prefix={'from_user_id': from_user_id}, reverse=True
        )
        for following in followings:
            if following.to_user_id == to_user_id:
                return following
        return None

    @classmethod
    def has_followed(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return False
        followings_id = cls.get_followings_id_set(from_user_id=from_user_id)
        return to_user_id in followings_id

    @classmethod
    def get_following_count(cls, from_user_id):
        followings_id = cls.get_followings_id_set(from_user_id=from_user_id)
        return len(followings_id)
