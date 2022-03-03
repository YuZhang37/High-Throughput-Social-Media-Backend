from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


# https://stackoverflow.com/questions/37722415/
# django-rest-framework-access-context-from-nested-serializer
# not found any official reference on how nested serializer works
class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(source='cached_tweet')

    class Meta:
        model = NewsFeed
        fields = ('id', 'user', 'tweet', 'created_at')
