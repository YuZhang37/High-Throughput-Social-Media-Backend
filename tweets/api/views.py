from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from newsfeeds.services import NewsFeedServices
from tweets.api.serializers import (
    TweetSerializerForCreate,
    TweetSerializerForList,
    TweetSerializerForCreateResponse
)
from tweets.models import Tweet


class TweetViewSet(GenericViewSet):

    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def list(self, request: Request):
        if 'user_id' not in request.query_params:
            return Response({
                "message": "missing user_id",
            }, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.query_params['user_id']
        if not get_user_model().objects.filter(id=user_id).exists():
            return Response({
                "message": "user doesn't exist",
            }, status=status.HTTP_400_BAD_REQUEST)
        tweets = Tweet.objects.filter(user=user_id).order_by("-created_at")
        serializer = TweetSerializerForList(tweets, many=True)
        return Response({
            "tweets": serializer.data
        }, status=status.HTTP_200_OK)

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
        NewsFeedServices.fan_out_to_followers(tweet)
        return Response(
            TweetSerializerForCreateResponse(tweet).data,
            status=status.HTTP_201_CREATED
        )
