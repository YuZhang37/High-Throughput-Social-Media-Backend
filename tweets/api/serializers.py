from django.contrib.auth import get_user_model
from rest_framework import serializers

from comments.api.serializers import CommentSerializer
from core.api.serializers import SimpleUserSerializerWithEmail
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


# clean tweet information only from itself
class TweetSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail()

    class Meta:
        model = Tweet
        fields = ['id', 'user',  'created_at', 'content']


# tweet information with likes and comments
class TweetSerializerWithDetail(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail()
    comments = CommentSerializer(source='comment_set', many=True)

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'comments', 'created_at', 'content']