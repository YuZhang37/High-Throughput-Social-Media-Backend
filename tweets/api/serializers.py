from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from comments.api.serializers import CommentSerializer
from comments.models import Comment
from core.api.serializers import SimpleUserSerializerWithEmail
from likes.api.serializers import LikeSerializer
from likes.models import Like
from likes.services import LikeService
from tweets.models import Tweet


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=1, max_length=140)

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
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = [
            'id',
            'user',
            'created_at',
            'content',
            'has_liked',
            'likes_count',
            'comments_count',
        ]

    def get_has_liked(self, obj):
        has_liked = LikeService.has_liked(
            user=self.context['request'].user,
            obj=obj,
        )
        return has_liked

    def get_likes_count(self, obj: Tweet):
        return obj.like_set.count()
        # count = Like.objects.filter(
        #     content_type=ContentType.objects.get_for_model(Tweet),
        #     object_id=obj.id
        # ).count()
        # return count

    def get_comments_count(self, obj: Tweet):
        return obj.comment_set.count()


# tweet information with likes and comments
class TweetSerializerWithDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = [
            'id',
            'user',
            'created_at',
            'content',
            'has_liked',
            'likes_count',
            'comments_count',
            'likes',
            'comments',
        ]