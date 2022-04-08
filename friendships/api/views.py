from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from friendships.api.serializers import (
    FriendshipSerializerForFollowers,
    FriendshipSerializerForFollowings,
    FriendshipSerializerForCreate,
)
from friendships.models import HBaseFollower, HBaseFollowing
from friendships.models import Friendship
from friendships.services import FriendshipService
from gatekeeper.gate_keeper import GateKeeper
from gatekeeper.service_names import SWITCH_FRIENDSHIP_TO_HBASE
from utils.paginations import EndlessPagination


class FriendshipViewSet(GenericViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = FriendshipSerializerForCreate
    pagination_class = EndlessPagination

    # followers and followings need to access the database, less frequent operations
    
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        user = get_user_model().objects.filter(id=pk)
        if not user:
            return Response({
                "success": False,
                "message": f"User with user_id = {pk} doesn't exist"
            }, status=status.HTTP_404_NOT_FOUND)

        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            friendships = Friendship.objects.filter(to_user=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)
        else:
            page = self.paginator.paginate_hbase(
                hbase_model=HBaseFollower, request=request, key_prefix=pk
            )
        serializer = FriendshipSerializerForFollowers(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(data=serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        user = get_user_model().objects.filter(id=pk)
        if not user:
            return Response({
                "success": False,
                "message": f"User with user_id = {pk} doesn't exist"
            }, status=status.HTTP_404_NOT_FOUND)

        if not GateKeeper.is_switch_on(SWITCH_FRIENDSHIP_TO_HBASE):
            friendships = Friendship.objects.filter(from_user=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)
        else:
            page = self.paginator.paginate_hbase(
                hbase_model=HBaseFollowing, request=request, key_prefix=pk
            )
        serializer = FriendshipSerializerForFollowings(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(data=serializer.data)

    # follow and unfollow need to access the database, but frequent operations

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request: Request, pk):
        to_user = self.get_object()
        from_user = request.user
        if from_user.id == to_user.id:
            return Response({
                "success": False,
                "message": "You cannot follow yourself."
            }, status=status.HTTP_400_BAD_REQUEST)
        if FriendshipService.has_followed(
                from_user_id=from_user.id, to_user_id=to_user.id
        ):
            return Response({
                "success": True,
                "duplicate": True,
            }, status=status.HTTP_201_CREATED)

        data = {'from_user_id': from_user.id, 'to_user_id': to_user.id}
        serializer = FriendshipSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        friendship = serializer.save()
        return Response({
            "success": True,
            "following": FriendshipSerializerForFollowings(
                friendship, context={'request': request},
            ).data
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request: Request, pk):
        to_user = self.get_object()
        from_user = request.user
        if from_user.id == to_user.id:
            return Response({
                "success": False,
                "message": "You cannot unfollow yourself."
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = FriendshipService.unfollow(from_user.id, to_user.id)
        return Response({
            "success": True,
            "deleted": deleted,
        }, status=status.HTTP_200_OK)

