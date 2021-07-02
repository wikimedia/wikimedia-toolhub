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
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import permissions
from rest_framework import viewsets

import reversion

from toolhub.apps.auditlog.context import auditlog_context
from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.versioned.models import RevisionMetadata
from toolhub.permissions import ObjectPermissionsOrAnonReadOnly

from .models import ToolList
from .models import ToolListItem
from .serializers import CreateToolListSerializer
from .serializers import ToolListDetailSerializer
from .serializers import ToolListSerializer
from .serializers import UpdateToolListSerializer


@extend_schema_view(
    create=extend_schema(
        description=_("""Create a new list of tools."""),
        request=CreateToolListSerializer,
        responses=ToolListDetailSerializer,
    ),
    retrieve=extend_schema(
        description=_("""Details of a specific list of tools."""),
        responses=ToolListDetailSerializer,
    ),
    update=extend_schema(
        description=_("""Update a list of tools."""),
        request=UpdateToolListSerializer,
        responses=ToolListDetailSerializer,
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
    filterset_fields = {
        "featured": ["exact"],
        "published": ["exact"],
    }
    ordering = ["-id"]

    def get_queryset(self):
        """Filter qs by current user when editing."""
        user = self.request.user
        if not user.is_authenticated:
            user = None
        qs = ToolList.objects.filter(favorites=False)
        if self.request.method not in permissions.SAFE_METHODS:
            return qs.filter(created_by=user)
        qs = qs.filter(Q(published=True) | Q(created_by=user))
        return qs

    def get_serializer_class(self):
        """Use different serializers for input vs output."""
        if self.action == "retrieve":
            return ToolListDetailSerializer
        if self.action == "create":
            return CreateToolListSerializer
        if self.action == "update":
            return UpdateToolListSerializer
        return ToolListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """Create a new tool list."""
        user = self.request.user
        comment = serializer.validated_data.pop("comment", None)
        tools = serializer.validated_data.pop("tools", None)
        serializer.validated_data["created_by"] = user
        serializer.validated_data["modified_by"] = user

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(user)
            if comment is not None:
                reversion.set_comment(comment)

            with auditlog_context(user, comment):
                instance = ToolList.objects.create(**serializer.validated_data)
                for idx, name in enumerate(tools):
                    ToolListItem.objects.create(
                        toollist=instance,
                        tool=Tool.objects.get(name=name),
                        order=idx,
                        added_by=user,
                    )

        serializer.instance = instance
        return instance

    @transaction.atomic
    def perform_update(self, serializer):
        """Update a tool list."""
        user = self.request.user
        comment = serializer.validated_data.pop("comment", None)
        tools = serializer.validated_data.pop("tools", None)

        # Compute changes to the list metadata
        instance_has_changes = False
        for key, value in serializer.validated_data.items():
            prior = getattr(serializer.instance, key)
            if value != prior:
                setattr(serializer.instance, key, value)
                instance_has_changes = True

        # Compute changes to the list contents
        list_qs = ToolListItem.objects.filter(toollist=serializer.instance)
        prior_tools = list(list_qs.values_list("tool__name", flat=True))
        # I thought about doing some really fancy list diffing here using
        # difflib.SequenceMatcher to find the minimal set of changes to the
        # list items so that the db update could be really targeted. After
        # playing with the idea it felt like a big pile of overkill, so
        # instead we will just compare the ordered lists and if anything is
        # different replace all of it below.
        list_has_changes = prior_tools != tools

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(user)
            if comment is not None:
                reversion.set_comment(comment)

            with auditlog_context(user, comment):
                if instance_has_changes:
                    serializer.instance.modified_by = user
                    serializer.instance.save()

                if list_has_changes:
                    # Delete prior list contents and then repopulate
                    list_qs.delete()
                    for idx, name in enumerate(tools):
                        ToolListItem.objects.create(
                            toollist=serializer.instance,
                            tool=Tool.objects.get(name=name),
                            order=idx,
                            added_by=user,
                        )
