from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'first_name',
                  'last_name', 'email', 'password']

