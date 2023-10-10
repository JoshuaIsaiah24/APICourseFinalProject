from rest_framework import permissions
from rest_framework import response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class UserReadOnlyPermission(IsAuthenticatedOrReadOnly):
    pass


class ManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Manager').exists()
    
class DeliveryCrewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Delivery-crew').exists()
    