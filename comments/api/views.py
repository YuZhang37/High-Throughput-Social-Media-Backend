from django.shortcuts import render
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
        return Response({
            "success": True,
            "comment": CommentSerializer(comment).data,
        }, status=status.HTTP_201_CREATED)

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
            "data": CommentSerializer(comment).data,
        }, status=status.HTTP_200_OK)

    def destroy(self, request: Request, pk):
        instance = self.get_object()
        instance.delete()
        return Response({
            "success": True,
        }, status=status.HTTP_200_OK)

    @required_params(params=['tweet_id', ])
    def list(self, request: Request):
        # tweet_id = request.query_params['tweet_id']
        # comments = self.queryset.filter(tweet=tweet_id).order_by("created_at")
        comments = self.filter_queryset(self.queryset).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "comments": serializer.data,
        }, status=status.HTTP_200_OK)




