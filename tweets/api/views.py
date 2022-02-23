from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from newsfeeds.services import NewsFeedServices
from tweets.api.serializers import (
    TweetSerializerForCreate,
    TweetSerializerWithDetail,
    TweetSerializer,
)
from tweets.models import Tweet
from utils.decorators import required_params


class TweetViewSet(GenericViewSet):

    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

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
        tweets = Tweet.objects.filter(user=user_id).order_by("-created_at")
        serializer = TweetSerializer(tweets, many=True)
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
            TweetSerializer(tweet).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request: Request, pk):
        tweet = self.get_object()
        serializer = TweetSerializerWithDetail(tweet)
        return Response({
            "tweet": serializer.data,
        }, status=status.HTTP_200_OK)
