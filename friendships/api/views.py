from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.viewsets import GenericViewSet

from friendships.api.paginations import FriendshipPagination
from friendships.api.serializers import (
    EmptyFriendshipSerializer,
    FriendshipSerializerForFollowers,
    FriendshipSerializerForFollowings,
)
from friendships.models import Friendship
from friendships.services import FriendshipService


class FriendshipViewSet(GenericViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = EmptyFriendshipSerializer
    pagination_class = FriendshipPagination
    
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        self.get_object()
        friendships = Friendship.objects.filter(to_user=pk).order_by('-created_at')
        # when calling paginate_queryset(), pagination class will be instantiated
        # <for each request, there is a new instance of the viewset to serve the request
        # when the request is finished with a response, the instance is destroyed>
        page = self.paginate_queryset(friendships)
        serializer = FriendshipSerializerForFollowers(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(data=serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        self.get_object()
        friendships = Friendship.objects.filter(from_user=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FriendshipSerializerForFollowings(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(data=serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request: Request, pk):
        to_user = self.get_object()
        from_user = request.user
        if from_user.id == to_user.id:
            return Response({
                "success": False,
                "message": "You cannot follow yourself."
            }, status=status.HTTP_400_BAD_REQUEST)
        if Friendship.objects.filter(from_user=from_user.id, to_user=to_user.id).exists():
            return Response({
                "success": True,
                "duplicate": True,
            }, status=status.HTTP_201_CREATED)
        friendship = Friendship.objects.create(
            from_user=from_user, to_user=to_user
        )
        FriendshipService.invalidate_following_cache(from_user_id=from_user.id)
        # data = {'from_usr': from_user_id, 'to_user': to_user_id}
        # serializer = FriendshipSerializerForFollow(data=data)
        return Response({
            "success": True,
            "following": FriendshipSerializerForFollowings(
                friendship, context={'request': request},
            ).data
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request: Request, pk):
        to_user = self.get_object()
        from_user = request.user
        if from_user.id == to_user.id:
            return Response({
                "success": False,
                "message": "You cannot unfollow yourself."
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = Friendship.objects.filter(
            from_user=from_user.id,
            to_user=to_user.id,
        ).delete()
        if deleted:
            FriendshipService.invalidate_following_cache(
                from_user_id=from_user.id
            )
        return Response({
            "success": True,
            "deleted": deleted,
        }, status=status.HTTP_200_OK)

