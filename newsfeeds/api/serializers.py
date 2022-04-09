from rest_framework import serializers
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    tweet = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_tweet(self, obj):
        serializer = TweetSerializer(obj.cached_tweet, context=self.context)
        return serializer.data

    def get_created_at(self, obj):
        return obj.created_at
