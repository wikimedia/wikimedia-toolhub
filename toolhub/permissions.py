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


@rules.predicate
def is_obj_creator(user, obj=None):
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


# User group based permissions
is_administrator = rules.is_group_member("Administrators")
is_bureaucrat = rules.is_group_member("Bureaucrats")
is_oversighter = rules.is_group_member("Oversighters")
is_patroller = rules.is_group_member("Patrollers")
is_user = rules.is_group_member("Users")


# Convenience permission combinations
is_authed = rules.is_authenticated
is_obj_creator_or_admin = is_authed & (is_obj_creator | is_administrator)
is_obj_user_or_admin = is_authed & (is_obj_user | is_administrator)
is_self_or_admin = is_authed & (is_self | is_administrator)


# Configure permissions by app and model.
# Any of add, change, delete, view that are not set for a given model will
# default to rules.always_deny when the rules are applied.
MODEL_PERMISSIONS = {
    "auth": {  # django.contrib.auth
        "group": {
            "add": is_administrator,
            "change": is_bureaucrat | is_administrator,
            "delete": is_bureaucrat | is_administrator,
            "view": rules.always_allow,
        },
    },
    "crawler": {
        "url": {
            "add": is_authed,
            "change": is_obj_creator_or_admin,
            "delete": is_obj_creator_or_admin,
            "view": rules.always_allow,
        },
        "run": {
            "view": rules.always_allow,
        },
        "runurl": {
            "view": rules.always_allow,
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
            "view": is_obj_user_or_admin,
        },
    },
    "reversion": {  # https://github.com/etianen/django-reversion
        "version": {
            "add": is_authed,
            "view": rules.always_allow,
        },
    },
    "toolinfo": {
        "tool": {
            "add": is_authed,
            "change": is_obj_creator_or_admin,
            "delete": is_obj_creator_or_admin,
            "view": rules.always_allow,
        },
    },
    "user": {
        "toolhubuser": {
            "add": rules.always_deny,
            "change": is_obj_creator_or_admin,
            "delete": is_obj_creator_or_admin,
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


register_model_permissions(MODEL_PERMISSIONS)
