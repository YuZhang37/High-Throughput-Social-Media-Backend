from rest_framework import serializers

from core.api.serializers import SimpleUserSerializerWithEmail
from friendships.models import Friendship


class EmptyFriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = []


class FriendshipSerializerForFollowers(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail(source='from_user')

    class Meta:
        model = Friendship
        fields = ['user', 'created_at']


class FriendshipSerializerForFollowings(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail(source='to_user')

    class Meta:
        model = Friendship
        fields = ['user', 'created_at']


# class FriendshipSerializerForFollow(serializers.ModelSerializer):
#
#     class Meta:
#         model = Friendship
#         fields = ['from_user', 'to_user', 'created_at']