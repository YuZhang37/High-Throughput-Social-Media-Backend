from django.contrib.auth import get_user_model
from rest_framework import serializers

from friendships.models import Friendship


class EmptyFriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = []


class UserSerializerForFriendship(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']


class FriendshipSerializerForFollowers(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ['user', 'created_at']


class FriendshipSerializerForFollowings(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ['user', 'created_at']


# class FriendshipSerializerForFollow(serializers.ModelSerializer):
#
#     class Meta:
#         model = Friendship
#         fields = ['from_user', 'to_user', 'created_at']