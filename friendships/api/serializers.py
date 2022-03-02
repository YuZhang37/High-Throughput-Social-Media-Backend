from rest_framework import serializers

from core.api.serializers import SimpleUserSerializerWithEmail
from friendships.models import Friendship
from friendships.services import FriendshipService


class EmptyFriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = []


class FriendshipSerializerForFollowers(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['user', 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        return FriendshipService.has_followed(
            from_user=self.context['request'].user,
            to_user=obj.from_user,
        )


class FriendshipSerializerForFollowings(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail(source='to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['user', 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        return FriendshipService.has_followed(
            from_user=self.context['request'].user,
            to_user=obj.to_user,
        )
