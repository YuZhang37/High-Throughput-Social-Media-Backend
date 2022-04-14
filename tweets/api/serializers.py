
from rest_framework import serializers

from comments.api.serializers import CommentSerializer
from core.api.serializers import SimpleUserSerializerWithEmail
from likes.api.serializers import LikeSerializer
from likes.services import LikeService
from tweets.constants import TWEET_PHOTO_UPLOAD_LIMIT
from tweets.models import Tweet
from tweets.services import TweetPhotoService
from utils.redisUtils.redis_services import RedisService


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
    user = SimpleUserSerializerWithEmail(source='cached_user')
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

    def _get_liked_tweet_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_liked_tweet_id_set'):
            return self._cached_liked_tweet_id_set
        liked_tweet_id_set = LikeService.get_liked_objects_id_set(
            user_id=self.context['request'].user.id, model_class=Tweet
        )
        setattr(self, '_cached_liked_tweet_id_set', liked_tweet_id_set)
        return liked_tweet_id_set

    def get_has_liked(self, obj):
        if hasattr(self.context, '_cached_liked_tweet_id_set_from_newsfeed'):
            liked_tweet_id_set \
                = self.context['_cached_liked_tweet_id_set_from_newsfeed']
        else:
            liked_tweet_id_set = self._get_liked_tweet_id_set()
        return obj.id in liked_tweet_id_set

    def get_likes_count(self, obj: Tweet):
        count = RedisService.get_count(obj, 'likes_count')
        return count

    def get_comments_count(self, obj: Tweet):
        count = RedisService.get_count(obj, 'comments_count')
        return count

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
