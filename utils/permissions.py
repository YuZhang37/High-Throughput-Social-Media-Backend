from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsObjectOwner(BasePermission):
    message = "You do not have the permission to modify this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request: Request, view, obj):
        if request.user.id != obj.user.id:
            return False
        return True
