from rest_framework import serializers

from core.api.serializers import SimpleUserSerializerWithEmail
from core.services import UserService
from friendships.services import FriendshipService


class BaseFriendshipSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    has_followed = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def _following_user_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        following_user_id_set = FriendshipService.get_followings_id_set(
            from_user_id=self.context['request'].user.id
        )
        setattr(self, '_cached_following_user_id_set', following_user_id_set)
        return following_user_id_set

    def get_user_id(self, obj):
        raise NotImplementedError

    def get_user(self, obj):
        user = UserService.get_user_from_cache_with_user_id(self.get_user_id(obj))
        serializer = SimpleUserSerializerWithEmail(instance=user)
        return serializer.data

    def get_created_at(self, obj):
        return obj.created_at

    def get_has_followed(self, obj):
        following_user_id_set = self._following_user_id_set()
        return self.get_user_id(obj) in following_user_id_set


class FriendshipSerializerForFollowers(BaseFriendshipSerializer):

    def get_user_id(self, obj):
        return obj.from_user_id


class FriendshipSerializerForFollowings(BaseFriendshipSerializer):

    def get_user_id(self, obj):
        return obj.to_user_id


class FriendshipSerializerForCreate(serializers.Serializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        friendship = FriendshipService.follow(
            **validated_data
        )
        return friendship


