from rest_framework.permissions import *


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user == obj.owner or request.user.is_stuff)
    

class IsCommentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return request.user.is_authenticated and (request.user == obj.owner)
        return request.user.is_authenticated and (request.user == obj.owner or request.user.is_stuff)