from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_authenticated_user(user):
    return bool(user and user.is_authenticated)


def is_verified_user(user):
    return bool(user and user.is_verified)


def is_active_user(user):
    return bool(user and user.is_active)


def is_admin_user(user):
    return bool(user and user.is_staff)


class IsVerifiedUser(BasePermission):
    def has_permission(self, request, view):
        return (
            is_authenticated_user(request.user)
            and is_verified_user(request.user)
        )


class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return (
            is_authenticated_user(request.user)
            and is_active_user(request.user)
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            is_authenticated_user(request.user)
            and is_admin_user(request.user)
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return getattr(obj, "user", None) == request.user


class IsSelfUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsVerifiedAndActiveUser(BasePermission):
    def has_permission(self, request, view):
        return (
            is_authenticated_user(request.user)
            and is_verified_user(request.user)
            and is_active_user(request.user)
        )


class IsAuthenticatedOnly(BasePermission):
    def has_permission(self, request, view):
        return is_authenticated_user(request.user)
    