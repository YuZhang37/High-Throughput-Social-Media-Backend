from rest_framework import serializers
from comments.models import Comment
from core.api.serializers import SimpleUserSerializer
from likes.services import LikeService
from tweets.models import Tweet
from utils.redisUtils.redis_services import RedisService


class CommentSerializerForCreate(serializers.ModelSerializer):
    tweet_id = serializers.IntegerField()
    content = serializers.CharField(max_length=140)

    class Meta:
        model = Comment
        fields = ['tweet_id', 'content']

    def validate(self, attrs):
        if not Tweet.objects.filter(id=attrs['tweet_id']).exists:
            raise serializers.ValidationError("tweet doesn't exist")
        attrs['user_id'] = self.context['request'].user.id
        return attrs

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        return comment


class CommentSerializerForUpdate(serializers.ModelSerializer):

    content = serializers.CharField(max_length=140)

    class Meta:
        model = Comment
        fields = ['content']

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(source='cached_user')
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'has_liked',
            'likes_count',
        ]

    def _get_liked_comment_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_liked_comments_id_set'):
            return self._cached_liked_comments_id_set
        liked_comments_id_set = LikeService.get_liked_objects_id_set(
            user_id=self.context['request'].user.id, model_class=Comment
        )
        setattr(self, '_cached_liked_comments_id_set', liked_comments_id_set)
        return liked_comments_id_set

    def get_likes_count(self, obj):
        count = RedisService.get_count(obj, 'likes_count')
        return count

    def get_has_liked(self, obj):
        liked_comments_id_set = self._get_liked_comment_id_set()
        return obj.id in liked_comments_id_set
