from notifications.models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):

    # TODO return actor and target with a meaningful representation
    class Meta:
        model = Notification
        fields = [
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'target_content_type',
            'target_object_id',
            'level',
            'recipient',
            'unread',
            'timestamp',
        ]


class NotificationSerializerForUpdate(serializers.ModelSerializer):

    unread = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ['unread', ]

    # the default update implementation is enough
    # def update(self, instance, validated_data):
    #     instance.unread = validated_data['unread']
    #     instance.save()
    #     return instance
