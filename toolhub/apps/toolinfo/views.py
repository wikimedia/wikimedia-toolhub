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
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

import jsonpatch

from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action

from reversion.models import Version

import spdx_license_list

from toolhub.apps.auditlog.models import LogEntry
from toolhub.apps.versioned.exceptions import ConflictingState
from toolhub.apps.versioned.exceptions import CurrentRevision
from toolhub.apps.versioned.exceptions import PatrolledRevision
from toolhub.apps.versioned.exceptions import SuppressedRevision
from toolhub.permissions import CustomModelPermission
from toolhub.permissions import ObjectPermissions
from toolhub.permissions import ObjectPermissionsOrAnonReadOnly
from toolhub.serializers import CommentSerializer

from .models import Annotations
from .models import Tool
from .serializers import AnnotationsSerializer
from .serializers import CreateToolSerializer
from .serializers import SpdxLicenseSerializer
from .serializers import ToolRevisionDetailSerializer
from .serializers import ToolRevisionDiffSerializer
from .serializers import ToolRevisionSerializer
from .serializers import ToolSerializer
from .serializers import UpdateAnnotationsSerializer
from .serializers import UpdateToolSerializer


logger = logging.getLogger(__name__)


@extend_schema_view(
    create=extend_schema(
        description=_("""Create a new tool."""),
        request=CreateToolSerializer,
        responses=ToolSerializer,
    ),
    retrieve=extend_schema(
        description=_("""Info for a specific tool."""),
    ),
    update=extend_schema(
        description=_("""Update info for a specific tool."""),
        request=UpdateToolSerializer,
        responses=ToolSerializer,
    ),
    partial_update=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        description=_("""Delete a tool."""),
    ),
    list=extend_schema(
        description=_("""List all tools."""),
    ),
)
class ToolViewSet(viewsets.ModelViewSet):
    """Tools."""

    queryset = Tool.objects.select_related("annotations").all()
    lookup_field = "name"
    filterset_fields = {
        "name": ["exact", "contains", "startswith", "endswith"],
    }
    ordering_fields = ["name", "modified_date"]
    ordering = ["-modified_date"]
    permission_classes = [ObjectPermissionsOrAnonReadOnly]

    def get_serializer_class(self):
        """Use different serializers for input vs output."""
        if self.request.method == "POST":
            return CreateToolSerializer
        if self.request.method == "PUT":
            return UpdateToolSerializer
        return ToolSerializer

    def _get_annotations_object(self):
        """Get the annotations object for the current tool."""
        qs = self.filter_queryset(self.get_queryset())
        tool = get_object_or_404(qs, name=self.kwargs["name"])
        obj = tool.annotations

        permission = ObjectPermissionsOrAnonReadOnly()
        required_perms = permission.get_required_object_permissions(
            self.request.method, obj.__class__
        )
        if not self.request.user.has_perms(required_perms, obj):
            self.permission_denied(
                self.request,
                message=getattr(permission, "message", None),
                code=getattr(permission, "code", None),
            )
        return obj

    @extend_schema(
        description=_("""Additional information for a tool."""),
        responses=AnnotationsSerializer,
    )
    @action(detail=True, methods=["GET"])
    def annotations(self, request, **kwargs):
        """Read the annotations model."""
        instance = self._get_annotations_object()
        serializer = AnnotationsSerializer(
            instance,
            context=self.get_serializer_context(),
        )
        return response.Response(serializer.data)

    @extend_schema(
        description=_("""Update annotations for a specific tool."""),
        request=UpdateAnnotationsSerializer,
        responses=AnnotationsSerializer,
    )
    @annotations.mapping.put
    def edit_annotations(self, request, **kwargs):
        """Edit the annotations model."""
        # Largely copied from rest_framework.mixins.UpdateModelMixin
        instance = self._get_annotations_object()
        serializer = UpdateAnnotationsSerializer(
            instance,
            data=request.data,
            partial=False,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return response.Response(serializer.data)


path_param_tool_name = OpenApiParameter(
    "tool_name",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    description=_("""Unique identifier for this tool."""),
)


@extend_schema_view(
    retrieve=extend_schema(
        description=_("""Get revision information."""),
        parameters=[path_param_tool_name],
        responses=ToolRevisionDetailSerializer,
    ),
    list=extend_schema(
        description=_("""List revisions."""),
        parameters=[path_param_tool_name],
        responses=ToolRevisionSerializer,
    ),
    diff=extend_schema(
        description=_("""Compare two revisions to find difference."""),
        parameters=[
            path_param_tool_name,
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
        responses=ToolRevisionDiffSerializer,
    ),
    revert=extend_schema(
        description=_("""Restore the tool to this revision."""),
        parameters=[
            path_param_tool_name,
        ],
        request=None,
        responses=ToolSerializer,
    ),
    undo=extend_schema(
        description=_("""Undo all changes made between two revisions."""),
        parameters=[
            path_param_tool_name,
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
        request=None,
        responses=ToolSerializer,
    ),
    hide=extend_schema(
        description=_("""Hide revision text and edit summary from users."""),
        parameters=[path_param_tool_name],
        request=CommentSerializer,
        responses={204: None},
    ),
    reveal=extend_schema(
        description=_("""Reveal a previously hidden revision."""),
        parameters=[path_param_tool_name],
        request=CommentSerializer,
        responses={204: None},
    ),
    patrol=extend_schema(
        description=_("""Mark a revision as patrolled."""),
        parameters=[path_param_tool_name],
        request=CommentSerializer,
        responses={204: None},
    ),
)
class ToolRevisionViewSet(viewsets.ReadOnlyModelViewSet):
    """Historical revisions of a tool."""

    queryset = Version.objects.none()
    serializer_class = ToolRevisionSerializer
    permission_classes = [ObjectPermissionsOrAnonReadOnly]

    def get_queryset(self):
        """Filter queryset by Tool using path param."""
        tool = get_object_or_404(Tool, name=self.kwargs["tool_name"])
        qs = Version.objects.select_related(
            "revision",
            "revision__user",
            "revision__meta",
        )
        qs = qs.get_for_object(tool)
        return qs

    def get_serializer_class(self):
        """Use different serializers for list vs retrieve."""
        if self.action == "retrieve":
            return ToolRevisionDetailSerializer
        return ToolRevisionSerializer

    def _get_historic_data(self, tool_version):
        """Get historic data for a given Tool version."""
        data = tool_version.field_dict

        data["annotations"] = {}
        qs = tool_version.revision.version_set.get_for_model(Annotations)
        ann = qs.first()
        if ann is not None:
            data["annotations"] = ann.field_dict

        return data

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

        data_left = ToolSerializer(self._get_historic_data(left)).data
        data_right = ToolSerializer(self._get_historic_data(right)).data
        # T279484: exclude modified_date from diff
        del data_left["modified_date"]
        del data_right["modified_date"]
        return jsonpatch.make_patch(data_left, data_right)

    @transaction.atomic
    def _update_tool(self, data, request):
        """Update our toolinfo record."""
        ctx = {"request": request}
        instance = get_object_or_404(Tool, name=self.kwargs["tool_name"])

        # Separate out annotations
        ann_data = data.pop("annotations", {})
        ann_data["comment"] = data["comment"]

        # Validate tool changes
        tool_ser = UpdateToolSerializer(instance, data=data, context=ctx)
        tool_ser.is_valid(raise_exception=True)

        # Validate annotations changes
        ann_ser = UpdateAnnotationsSerializer(
            instance.annotations, data=ann_data, context=ctx
        )
        ann_ser.is_valid(raise_exception=True)

        # Save both serializers. This may or may not save both models
        # depending on the diff of data to database state.
        tool = tool_ser.save()
        tool.annotations = ann_ser.save()

        return response.Response(ToolSerializer(tool).data)

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

        diff = ToolRevisionDiffSerializer(
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
        data = self._get_historic_data(rev)
        data["comment"] = _(
            "Revert to revision %(rev_id)s dated %(datetime)s by %(user)s"
        ) % {
            "rev_id": rev_id,
            "datetime": rev.revision.date_created.strftime(
                "%Y-%m-%dT%H:%M:%S.%f%z"
            ),
            "user": rev.revision.user.username,
        }
        return self._update_tool(data, request)

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

        head = qs.first()  # Most recent version
        data = self._get_historic_data(head)

        try:
            jsonpatch.apply_patch(data, patch, in_place=True)
        except jsonpatch.JsonPatchException as e:
            raise ConflictingState() from e

        data["comment"] = _(
            "Undo revisions from %(first_id)s to %(last_id)s"
        ) % {
            "first_id": id_left,
            "last_id": id_right,
        }
        return self._update_tool(data, request)

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
        with transaction.atomic():
            rev.revision.meta.suppressed = True
            rev.revision.meta.save()
            LogEntry.objects.log_action(
                request.user,
                rev,
                LogEntry.HIDE,
                comment,
                params={
                    "tool_name": self.kwargs["tool_name"],
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
        with transaction.atomic():
            rev.revision.meta.suppressed = False
            rev.revision.meta.save()
            LogEntry.objects.log_action(
                request.user,
                rev,
                LogEntry.REVEAL,
                comment,
                params={
                    "tool_name": self.kwargs["tool_name"],
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
        qs = self.get_queryset()
        rev = get_object_or_404(qs, pk=rev_id)
        if rev.revision.meta.patrolled:
            raise PatrolledRevision()
        comment = request.data.get("comment", None)
        with transaction.atomic():
            rev.revision.meta.patrolled = True
            rev.revision.meta.save()
            LogEntry.objects.log_action(
                request.user,
                rev,
                LogEntry.PATROL,
                comment,
                params={
                    "tool_name": self.kwargs["tool_name"],
                },
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    retrieve=extend_schema(
        description=_("""Info for a specific SPDX license."""),
        request=SpdxLicenseSerializer,
        responses=SpdxLicenseSerializer,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH),
        ],
    ),
    list=extend_schema(
        description=_("""List all SPDX licenses."""),
        request=SpdxLicenseSerializer,
        responses=SpdxLicenseSerializer,
        parameters=[
            OpenApiParameter(
                "osi_approved", OpenApiTypes.BOOL, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "fsf_approved", OpenApiTypes.BOOL, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "deprecated", OpenApiTypes.BOOL, OpenApiParameter.QUERY
            ),
        ],
    ),
)
class SpdxViewSet(viewsets.ViewSet):
    """SPDX license information."""

    def _as_bool(self, value):
        """Cast a value to a boolean."""
        return str(value).lower() in ["true", "1", "yes"]

    def _filter_bool(self, request, src, qs, field):
        """Apply a boolean filter to a dict of licenses."""
        qs = request.query_params.get(qs, None)
        if qs is not None:
            qs = self._as_bool(qs)
            src = {k: v for k, v in src.items() if v[field] == qs}
        return src

    def list(self, request):  # noqa: A003
        """Get a list of license objects."""
        licenses = spdx_license_list.LICENSES
        licenses = self._filter_bool(
            request, licenses, "osi_approved", "isOsiApproved"
        )
        licenses = self._filter_bool(
            request, licenses, "fsf_approved", "isFsfLibre"
        )
        licenses = self._filter_bool(
            request, licenses, "deprecated", "isDeprecatedLicenseId"
        )

        serializer = SpdxLicenseSerializer(licenses.values(), many=True)
        return response.Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get a single license object."""
        licenses = spdx_license_list.LICENSES
        try:
            serializer = SpdxLicenseSerializer(licenses[pk])
            return response.Response(serializer.data)
        except KeyError:
            return response.Response(
                {
                    "code": 4004,
                    "message": "Not found.",
                    "status_code": 404,
                    "errors": [
                        {"field": "detail", "message": "Not found."},
                    ],
                },
                status=status.HTTP_404_NOT_FOUND,
            )
