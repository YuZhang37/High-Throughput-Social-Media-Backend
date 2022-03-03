from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from comments.models import Comment
from core.api.serializers import SimpleUserSerializer
from likes.models import Like
from likes.services import LikeService
from tweets.models import Tweet


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

    def get_likes_count(self, obj):
        content_type = ContentType.objects.get_for_model(Comment)
        count = Like.objects.filter(
            content_type=content_type,
            object_id=obj.id,
        ).count()
        return count

    def get_has_liked(self, obj):
        has_liked = LikeService.has_liked(
            user=self.context['request'].user,
            obj=obj,
        )
        return has_liked
