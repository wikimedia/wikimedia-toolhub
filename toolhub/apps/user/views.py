# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Toolhub is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Toolhub.  If not, see <http://www.gnu.org/licenses/>.
import urllib.parse

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import Group
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from toolhub.permissions import ObjectPermissions
from toolhub.permissions import ObjectPermissionsOrAnonReadOnly
from toolhub.permissions import casl_for_user

from .models import ToolhubUser
from .serializers import AuthTokenSerializer
from .serializers import CurrentUserSerializer
from .serializers import GroupDetailSerializer
from .serializers import GroupSerializer
from .serializers import LocaleSerializer
from .serializers import UserDetailSerializer


class CurrentUserView(APIView):
    """User info."""

    @extend_schema(
        description=_(
            """Get information about the currently logged in user."""
        ),
        responses=CurrentUserSerializer,
    )
    def get(self, request):
        """Get info."""
        user = request.user
        user_info = {
            "id": user.id,
            "username": user.get_username(),
            "email": getattr(user, "email", None),
            "is_active": user.is_active,
            "is_anonymous": user.is_anonymous,
            "is_authenticated": user.is_authenticated,
            "is_staff": user.is_staff,
            "csrf_token": get_token(request),
            "casl": casl_for_user(user),
        }
        serializer = CurrentUserSerializer(user_info)
        return Response(serializer.data)


class LocaleView(APIView):
    """User's locale."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description=_("""Get current locale."""),
        responses=LocaleSerializer,
    )
    def get(self, request):
        """Get locale."""
        locale = {
            "language": get_language(),
        }
        return Response(LocaleSerializer(locale).data)

    @extend_schema(
        description=_("""Set locale."""),
        request=LocaleSerializer,
        responses=LocaleSerializer,
    )
    def post(self, request):
        """Set locale."""
        serializer = LocaleSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(  # noqa: A003
        description=_("""List all active users."""),
    ),
    retrieve=extend_schema(
        description=_("""Info for a specific user."""),
    ),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Toolhub users."""

    queryset = ToolhubUser.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    permission_classes = [ObjectPermissionsOrAnonReadOnly]
    filterset_fields = {
        "id": ["gt", "gte", "lt", "lte"],
        "username": ["exact", "contains", "startswith", "endswith"],
        "date_joined": ["date__gt", "date__gte", "date__lt", "date__lte"],
        "groups__id": ["exact"],
    }
    ordering_fields = ["id", "username", "date_joined"]
    ordering = ["-date_joined"]


@extend_schema_view(
    list=extend_schema(
        description=_("""List all user groups."""),
    ),
    retrieve=extend_schema(
        description=_("""Info for a user group."""),
        responses=GroupDetailSerializer,
    ),
)
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Django user groups."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [ObjectPermissionsOrAnonReadOnly]
    ordering_fields = ["id", "name"]
    ordering = ["id"]

    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == "retrieve":
            return GroupDetailSerializer
        return GroupSerializer


@extend_schema_view(
    update=extend_schema(
        description=_("""Add a user to this group."""),
        parameters=[
            OpenApiParameter(
                "group_pk",
                OpenApiTypes.NUMBER,
                OpenApiParameter.PATH,
            ),
        ],
    ),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(
        description=_("""Remove a user from this group."""),
        parameters=[
            OpenApiParameter(
                "group_pk",
                OpenApiTypes.NUMBER,
                OpenApiParameter.PATH,
            ),
        ],
    ),
)
class GroupMembersViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Django group membership."""

    queryset = ToolhubUser.objects.none()
    serializer_class = GroupDetailSerializer
    permission_classes = [ObjectPermissions]
    lookup_field = "id"

    def get_queryset(self):
        """Get a queryset filtered to the appropriate objects."""
        return Group.objects.filter(pk=self.kwargs["group_pk"])

    def update(self, request, *args, **kwargs):  # noqa: W0613
        """Add a user to the group."""
        group = get_object_or_404(Group, pk=kwargs["group_pk"])
        user = get_object_or_404(ToolhubUser, id=kwargs["id"])
        group.user_set.add(user)
        serializer = self.get_serializer(instance=group)
        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):  # noqa: W0613
        """Remove a user from the group."""
        group = get_object_or_404(Group, pk=kwargs["group_pk"])
        user = get_object_or_404(ToolhubUser, id=kwargs["id"])
        group.user_set.remove(user)
        serializer = self.get_serializer(instance=group)
        return response.Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        description=_("""Get authentication token."""),
    ),
    post=extend_schema(
        description=_("""Create authentication token."""),
    ),
    delete=extend_schema(
        description=_("""Delete authentication token."""),
    ),
)
class AuthTokenView(generics.GenericAPIView):
    """API auth tokens for user-only bots."""

    serializer_class = AuthTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get a queryset filtered to the current user."""
        return Token.objects.filter(user=self.request.user)

    def get_object(self):
        """Get the user's authtoken or raise a 404."""
        obj = get_object_or_404(self.get_queryset())
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        """Get auth token."""
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Create auth token if none exists."""
        obj, _ = Token.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """Revoke auth token if it exists."""
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def login(request):  # noqa: W0613 unused argument
    """Start the login process."""
    return redirect(
        "{}?{}".format(
            reverse("social:begin", kwargs={"backend": "wikimedia"}),
            urllib.parse.urlencode({"next": request.GET.get("next", "/")}),
        )
    )


def logout(request):
    """End the user's session."""
    auth_logout(request)
    return redirect(reverse("vue:main"))
