from rest_framework import serializers

from core.api.serializers import SimpleUserSerializerWithEmail
from friendships.models import Friendship
from friendships.services import FriendshipService


class FollowingUserIdMixin:

    # object-level caching is important for following_user_id_set, since
    # in one query, we will serialize lots of friendships,
    # has_followed will be referenced to many times.
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        following_user_id_set = FriendshipService.get_followings_id_set(
            from_user_id=self.context['request'].user.id
        )
        setattr(self, '_cached_following_user_id_set', following_user_id_set)
        return following_user_id_set


class EmptyFriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = []


class FriendshipSerializerForFollowers(
    serializers.ModelSerializer,
    FollowingUserIdMixin,
):
    user = SimpleUserSerializerWithEmail(source='cached_from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['user', 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        # can't use obj.from_user.id, it will issue a query
        return obj.from_user_id in self.following_user_id_set


class FriendshipSerializerForFollowings(
    serializers.ModelSerializer,
    FollowingUserIdMixin,
):
    user = SimpleUserSerializerWithEmail(source='cached_to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['user', 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        return obj.to_user_id in self.following_user_id_set
