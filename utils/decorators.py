from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def required_params(method='GET', params=None):

    if method.lower() == 'get':
        request_attr = 'query_params'
    else:
        request_attr = 'data'

    if params is None:
        params = []

    def decorator(view_func):

        @wraps(view_func)
        def wrapped_view(instance, request):
            data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    "success": False,
                    "message": f'{params_str} are missing.'
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request)
        return wrapped_view
    return decorator
