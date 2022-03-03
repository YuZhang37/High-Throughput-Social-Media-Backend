from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from comments.models import Comment
from core.api.serializers import SimpleUserSerializer
from likes.models import Like
from tweets.models import Tweet


class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):

    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])

    class Meta:
        model = Like
        fields = ['object_id', 'content_type']

    def _get_model_class(self, content_type):
        if content_type == 'comment':
            return Comment
        elif content_type == 'tweet':
            return Tweet
        return None

    def validate(self, attrs):
        content_type = self._get_model_class(attrs['content_type'])
        if content_type is None:
            raise serializers.ValidationError({
                'content_type': f'{attrs["content_type"]} is not a valid choice'
            })
        if not content_type.objects.filter(id=attrs['object_id']).exists():
            raise serializers.ValidationError({
                'object_id': "Object does not exist."
            })
        attrs['content_type'] = ContentType.objects.get_for_model(content_type)
        attrs['user'] = self.context['request'].user
        return attrs


class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):

    def create(self, validated_data):
        instance = Like.objects.create(
            content_type=validated_data['content_type'],
            object_id=validated_data['object_id'],
            user=validated_data['user']
        )
        return instance


class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):

    def cancel(self):
        deleted, _ = Like.objects.filter(
            content_type=self.validated_data['content_type'],
            object_id=self.validated_data['object_id'],
            user=self.validated_data['user']
        ).delete()
        return deleted


class LikeSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(source='cached_user')

    class Meta:
        model = Like
        fields = ['user', 'created_at', ]
