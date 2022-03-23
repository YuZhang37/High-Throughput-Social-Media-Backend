from django.shortcuts import render
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate
)
from comments.models import Comment
from inbox.services import NotificationService
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class CommentViewSet(viewsets.GenericViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializerForCreate
    filterset_fields = ['tweet_id', ]

    def get_permissions(self):
        if self.action in ['create', ]:
            return [IsAuthenticated()]
        elif self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def create(self, request: Request):
        serializer = CommentSerializerForCreate(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "message": "Please check input",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response({
            "success": True,
            "comment": CommentSerializer(
                instance=comment,
                context={'request': request},
            ).data,
        }, status=status.HTTP_201_CREATED)

    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request: Request, pk):
        instance = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=instance, data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "message": "Please check input",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        return Response({
            "success": True,
            "data": CommentSerializer(
                instance=comment,
                context={'request': request},
            ).data,
        }, status=status.HTTP_200_OK)

    # destroy is easier than create and update, more frequently in a unit time,
    # but a less frequent operation
    @method_decorator(ratelimit(key='user', rate='5/s', method='POST', block=True))
    def destroy(self, request: Request, pk):
        instance = self.get_object()
        instance.delete()
        return Response({
            "success": True,
        }, status=status.HTTP_200_OK)

    @required_params(params=['tweet_id', ])
    @method_decorator(ratelimit(key='user', rate='10/s', method='GET', block=True))
    def list(self, request: Request):
        # tweet_id = request.query_params['tweet_id']
        # comments = self.queryset.filter(tweet=tweet_id).order_by("created_at")
        comments = self.filter_queryset(self.queryset).order_by('created_at')
        serializer = CommentSerializer(
            instance=comments,
            many=True,
            context={'request': request},
        )
        return Response({
            "comments": serializer.data,
        }, status=status.HTTP_200_OK)





