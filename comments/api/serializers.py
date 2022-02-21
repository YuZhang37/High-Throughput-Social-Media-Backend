from django.contrib.auth import get_user_model
from rest_framework import serializers

from comments.models import Comment
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'tweet_id', 'user', 'content', 'created_at']
