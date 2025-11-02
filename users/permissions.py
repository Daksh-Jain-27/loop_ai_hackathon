from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    """
    Allows access only to users with the 'doctor' role.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and has the 'doctor' role
        return request.user and request.user.is_authenticated and request.user.role == 'doctor'