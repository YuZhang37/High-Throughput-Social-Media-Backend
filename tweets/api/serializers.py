from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from comments.api.serializers import CommentSerializer
from comments.models import Comment
from core.api.serializers import SimpleUserSerializerWithEmail
from likes.api.serializers import LikeSerializer
from likes.models import Like
from likes.services import LikeService
from tweets.constants import TWEET_PHOTO_UPLOAD_LIMIT
from tweets.models import Tweet
from tweets.services import TweetPhotoService


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=1, max_length=140)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Tweet
        fields = ['content', 'files']

    def validate(self, attrs):
        num_of_files = len(attrs.get('files', []))
        if num_of_files > TWEET_PHOTO_UPLOAD_LIMIT:
            raise serializers.ValidationError({
                "files": 'The number of uploaded files should not exceed '
                         '{}'.format(TWEET_PHOTO_UPLOAD_LIMIT)
            })
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        tweet = Tweet.objects.create(
            user=user,
            content=validated_data['content'],
        )
        if 'files' in validated_data:
            TweetPhotoService.create_tweet_photos(tweet, validated_data['files'])
        return tweet


# clean tweet information only from itself
class TweetSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializerWithEmail()
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    photo_urls = serializers.SerializerMethodField()

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
            'photo_urls',
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

    def get_photo_urls(self, obj: Tweet):
        urls = []
        for photo in obj.tweetphoto_set.all().order_by('order'):
            urls.append(photo.file.url)
        return urls


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
            'photo_urls',
        ]
