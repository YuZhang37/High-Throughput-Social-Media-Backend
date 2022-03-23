from django.utils.decorators import method_decorator
from notifications.models import Notification
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from inbox.api.serializers import (
    NotificationSerializerForUpdate,
    NotificationSerializer
)
from utils.decorators import required_params

from utils.permissions import IsNotificationRecipient


class NotificationViewSet(viewsets.GenericViewSet,
                          ListModelMixin):

    filterset_fields = ['unread', ]
    permission_classes = [IsAuthenticated, IsNotificationRecipient]
    # permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationSerializer
        return NotificationSerializerForUpdate

    # all the following there methods need to access the database
    @action(methods=['GET'], detail=False, url_path='unread-count')
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def unread_count(self, request, *args, **kwargs):
        count = self.get_queryset().filter(unread=True).count()
        return Response({
            'unread_count': count
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def mark_all_as_read(self, request, *args, **kwargs):
        updated = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({
            'marked_count': updated,
        }, status=status.HTTP_200_OK)

    @required_params(method='PUT', params=['unread'])
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = NotificationSerializerForUpdate(
            instance=instance,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response({
            'success': True,
            'notification': NotificationSerializer(instance).data
        }, status=status.HTTP_200_OK)

