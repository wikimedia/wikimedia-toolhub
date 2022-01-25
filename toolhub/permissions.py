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
from rest_framework import permissions

import rules


class ObjectPermissions(permissions.DjangoObjectPermissions):
    """Per object permissions checking for DRF."""

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class ObjectPermissionsOrAnonReadOnly(ObjectPermissions):
    """Per object permissions checking, plus allow anon read-only access."""

    authenticated_users_only = False


class CustomModelPermission(permissions.BasePermission):
    """Check a specific model permission."""

    def __init__(self, app_label, model_name, permission):
        """Initialize object."""
        self._perm = "{}.{}_{}".format(app_label, permission, model_name)

    def __call__(self):
        """Act like a callable so that DRF's plumbing works."""
        return self

    def has_permission(self, request, view):
        """Check permission."""
        return rules.permissions.has_perm(self._perm, request.user)

    def has_object_permission(self, request, view, obj):
        """Check object permission."""
        return rules.permissions.has_perm(self._perm, request.user, obj)

    def __repr__(self):
        """Object repr."""
        return "<{}:{} object at {}>".format(
            type(self).__name__,
            str(self),
            hex(id(self)),
        )

    def __str__(self):
        """String repr."""
        return ", ".join(self._perms)


@rules.predicate
def is_creator(user, obj=None):
    """Is the given user the creator of the given object?"""
    if obj is None:  # called via has_permission()
        return True
    if not hasattr(obj, "created_by"):
        return False
    return obj.created_by == user


@rules.predicate
def is_obj_user(user, obj=None):
    """Is the given user the 'user' of the given object?"""
    if obj is None:  # called via has_permission()
        return True
    if not hasattr(obj, "user"):
        return False
    return obj.user == user


@rules.predicate
def is_self(user, obj=None):
    """Is the given user the same as the given object?"""
    if obj is None:  # called via has_permission()
        return True
    return obj == user


@rules.predicate
def is_not_suppressed(user, obj=None):  # noqa: W0613
    """Is the given object suppressed?"""
    if obj is None:  # called via has_permission()
        return True

    # Check for objects which have a direct flag:
    if hasattr(obj, "suppressed"):
        return not obj.suppressed

    # Normally, suppression is recorded in the 'meta' model attached to
    # a 'revision' that collects 'versions' of one or more models that were
    # changed under revision tracking.
    if not hasattr(obj, "revision"):
        return False
    if not hasattr(obj.revision, "meta"):
        return False
    return not getattr(obj.revision.meta, "suppressed", False)


# User group based permissions
is_administrator = rules.is_group_member("Administrators")
is_bureaucrat = rules.is_group_member("Bureaucrats")
is_oversighter = rules.is_group_member("Oversighters")
is_patroller = rules.is_group_member("Patrollers")
is_admin_or_crat = is_bureaucrat | is_administrator
is_admin_or_oversighter = is_oversighter | is_administrator
is_admin_or_patroller = is_patroller | is_administrator

# Convenience permission combinations
is_authed = rules.is_authenticated
is_creator_or_admin = is_authed & (is_creator | is_administrator)
is_creator_or_oversighter = is_authed & (is_creator | is_admin_or_oversighter)
is_obj_user_or_admin = is_authed & (is_obj_user | is_administrator)
is_self_or_admin = is_authed & (is_self | is_administrator)
not_suppressed_or_is_oversighter = is_not_suppressed | is_admin_or_oversighter

# Configure permissions by app and model.
# Any of add, change, delete, view that are not set for a given model will
# default to rules.always_deny when the rules are applied.
MODEL_PERMISSIONS = {
    "auth": {  # django.contrib.auth
        "group": {
            "add": is_administrator,
            "change": is_admin_or_crat,
            "delete": is_admin_or_crat,
            "view": rules.always_allow,
        },
    },
    "crawler": {
        "url": {
            "add": is_authed,
            "change": is_creator_or_admin,
            "delete": is_creator_or_admin,
            "view": rules.always_allow,
        },
        "run": {
            "view": rules.always_allow,
        },
        "runurl": {
            "view": rules.always_allow,
        },
    },
    "lists": {
        "toollist": {
            "add": is_authed,
            "change": is_creator_or_oversighter,
            "delete": is_creator_or_admin,
            "view": rules.always_allow,
            "feature": is_administrator,
        },
    },
    "oauth2_provider": {  # https://github.com/jazzband/django-oauth-toolkit
        "application": {
            "add": is_authed,
            "change": is_obj_user_or_admin,
            "delete": is_obj_user_or_admin,
            "view": rules.always_allow,
        },
        "accesstoken": {
            "delete": is_obj_user_or_admin,
            "view": is_obj_user_or_admin,
        },
    },
    "reversion": {  # https://github.com/etianen/django-reversion
        "version": {
            "add": is_authed,
            "change": is_admin_or_oversighter,
            "delete": is_administrator,
            "view": not_suppressed_or_is_oversighter,
            "patrol": is_admin_or_patroller,
        },
    },
    "toolinfo": {
        "annotations": {
            "add": is_authed,
            "change": is_authed,
            "delete": is_administrator,
            "view": rules.always_allow,
        },
        "tool": {
            "add": is_authed,
            "change": is_creator_or_oversighter,
            "delete": is_creator_or_admin,
            "view": rules.always_allow,
        },
    },
    "user": {
        "toolhubuser": {
            "add": rules.always_deny,
            "change": is_self_or_admin,
            "delete": is_self_or_admin,
            "view": rules.always_allow,
        },
    },
}


def register_model_permissions(conf):
    """Register all configured model permissions."""

    def register(perms, app, model, action):
        """Register a rule."""
        name = "{}.{}_{}".format(app, action, model)
        # Unconditionally overwrite any existing state
        rules.set_perm(name, perms.get(action, rules.always_deny))

    for app, models in conf.items():
        if not rules.perm_exists(app):
            # Allow authenticated users to see admin section for this app
            rules.add_perm(app, rules.is_authenticated)
        for model, perms in models.items():
            register(perms, app, model, "add")
            register(perms, app, model, "change")
            register(perms, app, model, "delete")
            register(perms, app, model, "view")
            for perm in perms:
                if perm not in ["add", "change", "delete", "view"]:
                    register(perms, app, model, perm)


def casl_for_user(user):
    """Generate CASL authorization rules for the given user."""
    # CASL rules are sent to API consumers to help them understand if the
    # current user is allowed to perform certain actions. These rules can
    # largely be computed from our MODEL_PERMISSIONS base, but when things
    # enter the realm of per-instance permissions we need to send those rules
    # in a way that others can use rather than our backend predicates. We do
    # that by mapping predicates to rules here.

    def make_rule(user, perms, app, model, action):
        """Create a CASL rule."""
        predicate = perms.get(action, rules.always_deny)
        rule = {
            "subject": "{}/{}".format(app, model),
            "action": action,
        }
        if predicate in [
            is_creator,
            is_creator_or_admin,
            is_creator_or_oversighter,
            is_obj_user,
            is_obj_user_or_admin,
            is_self,
            is_self_or_admin,
        ]:
            # Complex predicates which require checking something about the
            # user's group membership and/or relationship to the object
            # instance.

            if not user.is_authenticated:
                rule["inverted"] = True

            else:
                if (
                    predicate == is_creator  # noqa: W0143
                    or (
                        predicate == is_creator_or_admin
                        and not is_administrator.test(user)
                    )
                    or (
                        predicate == is_creator_or_oversighter
                        and not is_admin_or_oversighter.test(user)
                    )
                ):
                    rule["conditions"] = {
                        "created_by.id": user.id,
                    }

                if predicate == is_obj_user or (  # noqa: W0143
                    predicate == is_obj_user_or_admin
                    and not is_administrator.test(user)
                ):
                    rule["conditions"] = {
                        "user.id": user.id,
                    }

                if predicate == is_self or (  # noqa: W0143
                    predicate == is_self_or_admin
                    and not is_administrator.test(user)
                ):
                    rule["conditions"] = {
                        "id": user.id,
                    }

        elif predicate == not_suppressed_or_is_oversighter and not (
            user.is_authenticated and is_admin_or_oversighter.test(user)
        ):
            # Special predicate combining payload and group membership checks.
            rule["conditions"] = {
                "suppressed": False,
            }

        else:
            # "Simple" predicate that we only need to extract the
            # user-based result from.
            if not predicate.test(user):
                # User is not allowed to take this action
                rule["inverted"] = True

        if (
            app == "toolinfo"
            and model == "tool"
            and action in ["change", "delete"]
        ):
            # Only API managed toolinfo records can be edited via API
            rule.setdefault("conditions", {})
            rule["conditions"]["origin"] = "api"

        return rule

    defaults = ["view", "add", "change", "delete"]
    casl = []
    for app, models in MODEL_PERMISSIONS.items():
        for model, perms in models.items():
            for action in defaults:
                casl.append(make_rule(user, perms, app, model, action))
            for perm in perms:
                if perm not in defaults:
                    casl.append(make_rule(user, perms, app, model, perm))

    # Filter out inverted rules. We don't need to state all the things that
    # cannot be done by the user, and we don't have any AND'd rules.
    return [rule for rule in casl if not rule.get("inverted", False)]


register_model_permissions(MODEL_PERMISSIONS)
