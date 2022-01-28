# Copyright (c) 2021 Wikimedia Foundation and contributors.
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
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

import jsonpatch

from rest_framework import permissions
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action

from reversion.models import Version

from toolhub.apps.auditlog.models import LogEntry
from toolhub.apps.toolinfo.serializers import SummaryToolSerializer
from toolhub.apps.versioned.exceptions import ConflictingState
from toolhub.apps.versioned.exceptions import CurrentRevision
from toolhub.apps.versioned.exceptions import SuppressedRevision
from toolhub.permissions import CustomModelPermission
from toolhub.permissions import ObjectPermissions
from toolhub.permissions import ObjectPermissionsOrAnonReadOnly
from toolhub.serializers import CommentSerializer

from .models import ToolList
from .models import ToolListItem
from .serializers import AddFavoriteSerializer
from .serializers import EditToolListSerializer
from .serializers import ToolListDiffSerializer
from .serializers import ToolListRevisionDetailSerializer
from .serializers import ToolListRevisionDiffSerializer
from .serializers import ToolListRevisionSerializer
from .serializers import ToolListSerializer


class ToolListFilter(filters.FilterSet):
    """Custom query filters for ToolList endpoints."""

    featured = filters.BooleanFilter(
        field_name="featured",
        lookup_expr="exact",
        help_text=_("Only show lists that are featured."),
    )
    published = filters.BooleanFilter(
        field_name="published",
        lookup_expr="exact",
        help_text=_("Only show lists that are published."),
    )
    user = filters.CharFilter(
        field_name="created_by__username",
        lookup_expr="exact",
        help_text=_("Only show lists created by the given user."),
    )


@extend_schema_view(
    create=extend_schema(
        description=_("""Create a new list of tools."""),
        request=EditToolListSerializer,
        responses=ToolListSerializer,
    ),
    retrieve=extend_schema(
        description=_("""Details of a specific list of tools."""),
        responses=ToolListSerializer,
    ),
    update=extend_schema(
        description=_("""Update a list of tools."""),
        request=EditToolListSerializer,
        responses=ToolListSerializer,
    ),
    partial_update=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        description=_("""Delete a list of tools."""),
    ),
    list=extend_schema(
        description=_("""List all lists of tools."""),
    ),
)
class ToolListViewSet(viewsets.ModelViewSet):
    """ToolLists"""

    queryset = ToolList.objects.none()
    serializer_class = ToolListSerializer
    permission_classes = [ObjectPermissionsOrAnonReadOnly]
    filterset_class = ToolListFilter
    ordering = ["-id"]

    def get_queryset(self):
        """Filter qs by current user when editing."""
        user = self.request.user
        if not user.is_authenticated:
            user = None
        qs = ToolList.objects.filter(favorites=False)
        if self.action in ["feature", "unfeature"]:
            featured_state = self.action == "unfeature"
            return qs.filter(published=True, featured=featured_state)
        if self.request.method not in permissions.SAFE_METHODS:
            # T287286: Administrators and Oversighters need to be able to
            # access all published lists for vandal fighting, so we cannot
            # limit to created_by=user here.
            return qs
        qs = qs.filter(Q(published=True) | Q(created_by=user))
        return qs

    def get_serializer_class(self):
        """Use different serializers for input vs output."""
        if self.action in ["create", "update"]:
            return EditToolListSerializer
        return ToolListSerializer

    @extend_schema(
        description=_("""Mark a list as featured."""),
        request=CommentSerializer,
        responses={204: None},
    )
    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"feature",
        permission_classes=[
            CustomModelPermission("lists", "toollist", "feature"),
        ],
    )
    def feature(self, request, **kwargs):  # noqa: W0613
        """Mark a list as featured."""
        instance = self.get_object()
        comment = request.data.get("comment", None)
        with transaction.atomic():
            instance.featured = True
            instance.save()
            LogEntry.objects.log_action(
                request.user,
                instance,
                LogEntry.FEATURE,
                comment,
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description=_("""Remove featured flag from a list."""),
        request=CommentSerializer,
        responses={204: None},
    )
    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"unfeature",
        permission_classes=[
            CustomModelPermission("lists", "toollist", "feature"),
        ],
    )
    def unfeature(self, request, **kwargs):  # noqa: W0613
        """Remove featured flag from a list."""
        instance = self.get_object()
        comment = request.data.get("comment", None)
        with transaction.atomic():
            instance.featured = False
            instance.save()
            LogEntry.objects.log_action(
                request.user,
                instance,
                LogEntry.UNFEATURE,
                comment,
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


path_param_list_pk = OpenApiParameter(
    "list_pk",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description=_("""A unique integer value identifying this toollist."""),
)


@extend_schema_view(
    retrieve=extend_schema(
        description=_("""Get revision information."""),
        parameters=[path_param_list_pk],
        responses=ToolListRevisionDetailSerializer,
    ),
    list=extend_schema(
        description=_("""List revisions."""),
        parameters=[path_param_list_pk],
        responses=ToolListRevisionSerializer,
    ),
    diff=extend_schema(
        description=_("""Compare two revisions to find difference."""),
        parameters=[
            path_param_list_pk,
            OpenApiParameter(
                "other_id",
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
                description=_(
                    "A unique integer value identifying version "
                    "to diff against."
                ),
            ),
        ],
        responses=ToolListRevisionDiffSerializer,
    ),
    revert=extend_schema(
        description=_("""Restore the list to this revision."""),
        parameters=[
            path_param_list_pk,
        ],
        responses=ToolListSerializer,
    ),
    undo=extend_schema(
        description=_("""Undo all changes made between two revisions."""),
        parameters=[
            path_param_list_pk,
            OpenApiParameter(
                "other_id",
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
                description=_(
                    "A unique integer value identifying version "
                    "to undo until."
                ),
            ),
        ],
        responses=ToolListSerializer,
    ),
    hide=extend_schema(
        description=_("""Hide revision text and edit summary from users."""),
        parameters=[path_param_list_pk],
        request=CommentSerializer,
        responses={204: None},
    ),
    reveal=extend_schema(
        description=_("""Reveal a previously hidden revision."""),
        parameters=[path_param_list_pk],
        request=CommentSerializer,
        responses={204: None},
    ),
    patrol=extend_schema(
        description=_("""Mark a revision as patrolled."""),
        parameters=[path_param_list_pk],
        request=CommentSerializer,
        responses={204: None},
    ),
)
class ToolListRevisionViewSet(viewsets.ReadOnlyModelViewSet):
    """Historical revisions of a tool list."""

    queryset = Version.objects.none()
    serializer_class = ToolListRevisionSerializer
    permission_classes = [ObjectPermissionsOrAnonReadOnly]

    def _get_list(self):
        """Get the list to act upon."""
        return get_object_or_404(ToolList, pk=self.kwargs["list_pk"])

    def get_queryset(self):
        """Filter queryset by ToolList using path param."""
        qs = Version.objects.select_related(
            "revision",
            "revision__user",
            "revision__meta",
        )
        return qs.get_for_object(self._get_list())

    def get_serializer_class(self):
        """Use different serializers for list vs retrieve."""
        if self.action == "retrieve":
            return ToolListRevisionDetailSerializer
        return ToolListRevisionSerializer

    def _get_patch(self, left, right, request):
        """Compute the JSON Patch between revisions."""
        # Our built-in permissions checking doesn't trigger on GET/HEAD
        # routes, so we need to explictly check that the calling user can see
        # the start and end revisions before preparing a patch.
        user = request.user
        perms = ["reversion.view_version"]
        if left.revision.meta.suppressed and not user.has_perms(perms, left):
            raise SuppressedRevision()
        if right.revision.meta.suppressed and not user.has_perms(perms, right):
            raise SuppressedRevision()

        data_left = ToolListDiffSerializer(left.field_dict).data
        data_right = ToolListDiffSerializer(right.field_dict).data
        return jsonpatch.make_patch(data_left, data_right)

    def _update_list(self, data, request):
        """Update our list record."""
        instance = get_object_or_404(ToolList, pk=self.kwargs["list_pk"])
        # Move the `tool_names` member to `tools` to match
        # EditToolListSerializer expectations for well formed input.
        data["tools"] = data.pop("tool_names", [])
        serializer = EditToolListSerializer(
            instance, data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return response.Response(ToolListSerializer(instance).data)

    @action(
        detail=True,
        methods=["GET"],
        url_path=r"diff/(?P<other_id>\d+)",
    )
    def diff(self, request, **kwargs):
        """Diff."""
        id_left = kwargs["pk"]
        id_right = kwargs["other_id"]
        qs = self.get_queryset()

        version_left = get_object_or_404(qs, pk=id_left)
        version_right = get_object_or_404(qs, pk=id_right)
        patch = self._get_patch(version_left, version_right, request)

        diff = ToolListRevisionDiffSerializer(
            {
                "original": version_left,
                "operations": patch,
                "result": version_right,
            },
            context={"request": request},
        )

        return response.Response(diff.data)

    @action(
        detail=True,
        methods=["POST"],
        url_path=r"revert",
    )
    def revert(self, request, **kwargs):
        """Revert."""
        rev_id = kwargs["pk"]
        qs = self.get_queryset()
        rev = get_object_or_404(qs, pk=rev_id)
        data = rev.field_dict
        data["comment"] = _(
            "Revert to revision %(rev_id)s dated %(datetime)s by %(user)s"
        ) % {
            "rev_id": rev_id,
            "datetime": rev.revision.date_created.strftime(
                "%Y-%m-%dT%H:%M:%S.%f%z"
            ),
            "user": rev.revision.user.username,
        }
        return self._update_list(data, request)

    @action(
        detail=True,
        methods=["POST"],
        url_path=r"undo/(?P<other_id>\d+)",
    )
    def undo(self, request, **kwargs):
        """Undo."""
        id_left = kwargs["pk"]
        id_right = kwargs["other_id"]
        qs = self.get_queryset()

        version_left = get_object_or_404(qs, pk=id_left)
        version_right = get_object_or_404(qs, pk=id_right)
        patch = self._get_patch(version_left, version_right, request)

        head = qs.first()
        data = head.field_dict

        try:
            # The operations on `tools` and `tool_names` below are needed to
            # coerce our live instance data into the shape expected by the
            # generated patch and then convert back to the shape expected by
            # the storage layer. It sure would be neat if the reversion
            # library had better built-in support for m2m relations!
            data["tools"] = data.get("tool_names", [])
            jsonpatch.apply_patch(data, patch, in_place=True)
            data["tool_names"] = data.get("tools", [])
        except jsonpatch.JsonPatchException as e:
            raise ConflictingState() from e

        data["comment"] = _(
            "Undo revisions from %(first_id)s to %(last_id)s"
        ) % {
            "first_id": id_left,
            "last_id": id_right,
        }
        return self._update_list(data, request)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"hide",
        permission_classes=[ObjectPermissions],
    )
    def hide(self, request, **kwargs):
        """Suppress a revision."""
        rev_id = int(kwargs["pk"])
        current_rev = self.get_queryset()[0]
        if current_rev.pk == rev_id:
            # The current revision cannot be hidden
            raise CurrentRevision()
        qs = self.get_queryset().filter(revision__meta__suppressed=False)
        rev = get_object_or_404(qs, pk=rev_id)
        comment = request.data.get("comment", None)
        active_list = self._get_list()
        with transaction.atomic():
            rev.revision.meta.suppressed = True
            rev.revision.meta.save()
            LogEntry.objects.log_action(
                request.user,
                rev,
                LogEntry.HIDE,
                comment,
                params={
                    "toollist": {
                        "id": active_list.pk,
                        "title": active_list.title,
                    },
                },
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"reveal",
        permission_classes=[ObjectPermissions],
    )
    def reveal(self, request, **kwargs):
        """Restore a suppressed revision."""
        rev_id = kwargs["pk"]
        qs = self.get_queryset().filter(revision__meta__suppressed=True)
        rev = get_object_or_404(qs, pk=rev_id)
        comment = request.data.get("comment", None)
        active_list = self._get_list()
        with transaction.atomic():
            rev.revision.meta.suppressed = False
            rev.revision.meta.save()
            LogEntry.objects.log_action(
                request.user,
                rev,
                LogEntry.REVEAL,
                comment,
                params={
                    "toollist": {
                        "id": active_list.pk,
                        "title": active_list.title,
                    },
                },
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"patrol",
        permission_classes=[
            CustomModelPermission("reversion", "version", "patrol"),
        ],
    )
    def patrol(self, request, **kwargs):
        """Mark a revision as patrolled."""
        rev_id = kwargs["pk"]
        qs = self.get_queryset().filter(revision__meta__patrolled=False)
        rev = get_object_or_404(qs, pk=rev_id)
        comment = request.data.get("comment", None)
        active_list = self._get_list()
        with transaction.atomic():
            rev.revision.meta.patrolled = True
            rev.revision.meta.save()
            LogEntry.objects.log_action(
                request.user,
                rev,
                LogEntry.PATROL,
                comment,
                params={
                    "toollist": {
                        "id": active_list.pk,
                        "title": active_list.title,
                    },
                },
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


path_param_tool_name = OpenApiParameter(
    "tool_name",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    description=_("""Unique identifier for this tool."""),
)


@extend_schema_view(
    create=extend_schema(
        description=_("""Add a tool to favorites."""),
        request=AddFavoriteSerializer,
        responses=SummaryToolSerializer,
    ),
    retrieve=extend_schema(
        description=_("""Check to see if a tool is in favorites."""),
        parameters=[path_param_tool_name],
        request=None,
        responses=SummaryToolSerializer,
    ),
    destroy=extend_schema(
        description=_("""Remove a tool from favorites."""),
        parameters=[path_param_tool_name],
        request=None,
        responses={204: None},
    ),
    list=extend_schema(
        description=_("""Personal favorites."""),
        responses=SummaryToolSerializer,
    ),
    partial_update=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class FavoritesViewSet(viewsets.ModelViewSet):
    """Personal favorites."""

    queryset = ToolListItem.objects.none()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "name"
    lookup_url_kwarg = "tool_name"

    def get_queryset(self):
        """Get the current user's favorites."""
        user = self.request.user
        favorites = ToolListItem.objects.get_user_favorites(user)
        if self.action == "destroy":
            # Delete needs to grab a ToolListItem object, not the tool it
            # points to.
            return ToolListItem.objects.filter(toollist=favorites.pk)
        return favorites.tools.all()

    def get_object(self):
        """Get the object(s) to operate on."""
        if self.action == "destroy":
            # No other way to vary lookup_field by action than a full
            # replacement of get_object.
            obj = get_object_or_404(
                self.filter_queryset(self.get_queryset()),
                tool__name=self.kwargs[self.lookup_url_kwarg],
            )
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def get_serializer_class(self):
        """Use different serializers for input vs output."""
        if self.action == "create":
            return AddFavoriteSerializer
        return SummaryToolSerializer

    def perform_create(self, serializer):
        """Add a tool to this user's favorites."""
        user = self.request.user
        serializer.save(
            toollist=ToolListItem.objects.get_user_favorites(user),
            order=0,
            added_by=user,
        )
