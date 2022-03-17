from django.conf import settings
from rest_framework import status
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from dateutil import parser


class EndlessPagination(BasePagination):
    has_next_page = False
    page_size = settings.ENDLESS_PAGINATION_SIZE

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False
        self.page_size = settings.ENDLESS_PAGINATION_SIZE

    def to_html(self):
        pass

    def paginate_cached_list(self, cached_list, request):
        self.has_next_page = False
        index = 0
        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            timestamp = parser.isoparse(created_at__gt)
            for index, tweet in enumerate(cached_list):
                if tweet.created_at <= timestamp:
                    break
            return cached_list[0: index]

        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            timestamp = parser.parse(created_at__lt)
            for index, tweet in enumerate(cached_list):
                if tweet.created_at < timestamp:
                    break
            else:
                return []
        if len(cached_list) - 1 >= index + self.page_size:
            self.has_next_page = True
        return cached_list[index: index + self.page_size]

    def paginate_queryset(self, queryset, request, view=None):
        self.has_next_page = False
        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt) \
                .order_by('-created_at')
            return queryset
        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt) \
                .order_by('-created_at')
        queryset = queryset[:self.page_size + 1]
        if len(queryset) > self.page_size:
            self.has_next_page = True
        return queryset[:self.page_size]

    def paginate_cached_list_with_limited_size(self, cached_list, request):
        page = self.paginate_cached_list(cached_list, request)
        if len(cached_list) < settings.REDIS_CACHED_LIST_LIMIT_LENGTH:
            return page
        if 'created_at__gt' in request.query_params:
            return page
        if self.has_next_page:
            return page
        return None

    def get_paginated_response(self, data):
        return Response({
            'has_next_page': self.has_next_page,
            'results': data,
        }, status=status.HTTP_200_OK)
