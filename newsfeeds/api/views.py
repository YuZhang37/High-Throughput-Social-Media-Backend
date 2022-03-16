from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from utils.paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):

    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request: Request):
        user = request.user
        newsfeed_list = self.queryset.filter(user=user)
        newsfeeds = self.paginate_queryset(newsfeed_list)
        serializer = NewsFeedSerializer(
            newsfeeds,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
