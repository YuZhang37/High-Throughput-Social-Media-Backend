from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import (
    TweetSerializerForCreate,
    TweetSerializerWithDetail,
    TweetSerializer,
)
from tweets.models import Tweet
from tweets.services import TweetService
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(GenericViewSet):

    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    @required_params(params=['user_id'])
    def list(self, request: Request):
        user_id = request.query_params['user_id']
        if not get_user_model().objects.filter(id=user_id).exists():
            return Response({
                "message": "user doesn't exist",
            }, status=status.HTTP_400_BAD_REQUEST)
        queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        tweet_list = TweetService.get_cached_tweets(user_id, queryset=queryset)
        page = self.paginator.paginate_cached_list_with_limited_size(
            tweet_list, request
        )
        if not page:
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request: Request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={"request": request}
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        tweet = serializer.save()
        NewsFeedService.fan_out_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request: Request, pk):
        tweet = self.get_object()
        serializer = TweetSerializerWithDetail(
            tweet,
            context={'request': request}
        )
        return Response({
            "tweet": serializer.data,
        }, status=status.HTTP_200_OK)
