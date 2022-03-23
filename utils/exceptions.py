from ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, Ratelimited):
        return Response({
            'detail': 'Too many requests',
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    return response
