from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(viewsets.GenericViewSet):

    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request: Request):
        user = request.user
        newsfeeds = self.queryset.filter(user=user)
        serializer = NewsFeedSerializer(newsfeeds, many=True)
        return Response({
            "newsfeeds": serializer.data,
        }, status=status.HTTP_200_OK)
