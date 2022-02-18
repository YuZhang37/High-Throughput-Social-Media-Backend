from django.contrib.auth import (
    logout as django_logout,
    login as django_login,
    authenticate as django_authenticate,
)

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets

from core.api.serializers import UserSerializer, SimpleUserSerializer, UserSerializerForLogin, UserSerializerForSignup
from core.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


# class AccountViewSet(viewsets.ViewSet):
# don't find official document for ViewSet to set serializer_class
class AccountViewSet(viewsets.GenericViewSet):

    # the default permission is set in settings.
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer

    @action(methods=['GET', ], detail=False)
    def login_status(self, request: Request):
        has_logged_in = request.user.is_authenticated
        data = {'has_logged_in': has_logged_in}
        if has_logged_in:
            user_data = SimpleUserSerializer(request.user).data
            data['user'] = user_data
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def logout(self, request: Request):
        django_logout(request)
        return Response({"success": True, }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False,
            serializer_class=UserSerializerForLogin)
    def login(self, request: Request):
        data = request.data
        serializer = UserSerializerForLogin(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = django_authenticate(username=username, password=password)
        # user = User.objects.get(username=username)
        if user is None:
            return Response({
                "success": False,
                "message": "Username and password does not match."
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            django_login(request, user)
            return Response({
                'success': True,
                'user': SimpleUserSerializer(user).data,
            }, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False,
            serializer_class=UserSerializerForSignup)
    def signup(self, request: Request):
        data = request.data
        serializer = UserSerializerForSignup(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input.",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': SimpleUserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


