from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from likes.API.serializers import LikeSerializerForCreate, LikeSerializer, LikeSerializerForCancel
from likes.models import Like
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializerForCreate
    permission_classes = [IsAuthenticated]

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
        return Response({
            "success": True,
            "like": LikeSerializer(like).data,
        }, status=status.HTTP_201_CREATED)
    # can use get_or_create in serializer.save(),
    # I choose this implementation because I want to return duplicated information

    @action(methods=['POST'], detail=False)
    @required_params(request_attr='data', params=['content_type', 'object_id'])
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