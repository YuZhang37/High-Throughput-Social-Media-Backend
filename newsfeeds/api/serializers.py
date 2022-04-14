from rest_framework import serializers

from likes.services import LikeService
from tweets.api.serializers import TweetSerializer
from tweets.models import Tweet


class NewsFeedSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    tweet = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def _get_liked_tweet_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if not hasattr(self, '_cached_liked_tweet_id_set'):
            liked_tweet_id_set = LikeService.get_liked_objects_id_set(
                user_id=self.context['request'].user.id,
                model_class=Tweet
            )
            setattr(self, '_cached_liked_tweet_id_set', liked_tweet_id_set)
        return getattr(self, '_cached_liked_tweet_id_set')

    def get_tweet(self, obj):
        if not hasattr(self.context, '_cached_liked_tweet_id_set_from_newsfeed'):
            self.context['_cached_liked_tweet_id_set_from_newsfeed'] \
                = self._get_liked_tweet_id_set()
        serializer = TweetSerializer(obj.cached_tweet, context=self.context)
        return serializer.data

    def get_created_at(self, obj):
        return obj.created_at
