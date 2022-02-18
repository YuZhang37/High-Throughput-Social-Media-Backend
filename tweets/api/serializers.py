from django.contrib.auth import get_user_model
from rest_framework import serializers

from tweets.models import Tweet


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ['content']

    def create(self, validated_data):
        user = self.context['request'].user
        tweet = Tweet.objects.create(
            user=user,
            content=validated_data['content'],
        )
        return tweet


class UserSerializerForTweetList(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class TweetSerializerForList(serializers.ModelSerializer):
    user = UserSerializerForTweetList()

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'created_at', 'content']


class UserSerializerForTweetCreateResponse(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']


class TweetSerializerForCreateResponse(serializers.ModelSerializer):
    user = UserSerializerForTweetCreateResponse()

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'created_at', 'content']