#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Spec object definition."""

from girder.constants import AccessType
from girder.models.model_base import AccessControlledModel
import datetime

# Example Spec object:
# {
#     "name": "inport",
#     "label": "InPort",
#     "description": "An input port for the graph",
#     "icon": "signin",
#     "driver": "GCCModelDriver",
#     "args": "unused",
#     "inports": [],
#     "outports": [
#         {"name": "value", "type": "all"}
#     ]
# }


class Spec(AccessControlledModel):
    """Defines the spec model."""

    def initialize(self):
        """Initialize the model."""
        self.name = 'spec'

        self.exposeFields(level=AccessType.READ, fields={
            '_id', 'name', 'created', 'content', 'description',
            'creatorId', 'public'})

    def validate(self, spec):
        """Validate the model."""
        return spec

    def list(self, user=None, limit=0, offset=0,
             sort=None, currentUser=None):
        """List a page of model specs for a given user.

        :param user: The user who owns the model spec.
        :type user: dict or None
        :param limit: The page limit.
        :param offset: The page offset
        :param sort: The sort field.
        :param currentUser: User for access filtering.
        """
        cursor_def = {}
        if user is not None:
            cursor_def['creatorId'] = user['_id']

        cursor = self.find(cursor_def, sort=sort)
        for r in self.filterResultsByPermission(
                cursor=cursor, user=currentUser, level=AccessType.READ,
                limit=limit, offset=offset):
            yield r

    def removeSpec(self, spec, token):
        """Remove a spec."""
        self.remove(spec)

    def createSpec(self, spec=None, creator=None, save=True):
        """Create a spec."""
        now = datetime.datetime.utcnow()

        obj = {
            'content': spec['content'],
            'hash': spec.get('hash', ''),
            'created': now,
            'creatorId': creator['_id']
        }

        if 'public' in spec and creator.get('admin'):
            self.setPublic(doc=obj, public=spec['public'])
        else:
            self.setPublic(doc=obj, public=False)

        if creator is not None:
            self.setUserAccess(obj, user=creator, level=AccessType.ADMIN,
                               save=False)

        if save:
            obj = self.save(obj)

        return obj

    def updateSpec(self, spec):
        """Update a spec.

        :param spec: The spec document to update.
        :type spec: dict
        :returns: The spec document that was edited.
        """
        spec['updated'] = datetime.datetime.utcnow()
        return self.save(spec)
