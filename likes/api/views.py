from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inbox.services import NotificationService
from likes.api.serializers import LikeSerializerForCreate, LikeSerializer, LikeSerializerForCancel
from likes.models import Like
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializerForCreate
    permission_classes = [IsAuthenticated]

    # more often to create likes than create tweets
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def create(self, request):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "messages": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = Like.objects.filter(**serializer.validated_data).first()
        if instance is not None:
            return Response({
                "success": True,
                "duplicated": True,
                "like": LikeSerializer(instance).data,
            }, status=status.HTTP_201_CREATED)

        like = serializer.save()
        NotificationService.send_like_notification(like)

        return Response({
            "success": True,
            "like": LikeSerializer(like).data,
        }, status=status.HTTP_201_CREATED)
    # can use get_or_create in serializer.save(),
    # I choose this implementation because I want to return duplicated information

    @action(methods=['POST'], detail=False)
    @required_params(method='POST', params=['content_type', 'object_id'])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def cancel(self, request):
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "messages": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = serializer.cancel()
        return Response({
            "success": True,
            "deleted": deleted,
        }, status=status.HTTP_200_OK)