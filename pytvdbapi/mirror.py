# -*- coding: utf-8 -*-

# Copyright 2011 - 2013 Björn Larsson

# This file is part of pytvdbapi.
#
# pytvdbapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pytvdbapi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pytvdbapi.  If not, see <http://www.gnu.org/licenses/>.

"""
A module for the management of thetvdb.com_ mirror servers.

.. _thetvdb.com: http://thetvdb.com
"""

import logging
import random

from pytvdbapi import error
from pytvdbapi.xmlhelpers import parse_xml


__all__ = ['TypeMask', 'Mirror', 'MirrorList']

# Module logger object
logger = logging.getLogger(__name__)


class TypeMask(object):
    """An enum like class with the mask flags for the mirrors"""
    XML = 1
    BANNER = 2
    ZIP = 4


class Mirror(object):
    """Stores data about a pytvdbapi.com mirror server"""

    def __init__(self, mirror_id, url, type_mask):
        self.mirror_id = mirror_id
        self.url = url
        self.type_mask = int(type_mask)

    def __repr__(self):
        return "<{0} ({1}:{2})>".format("Mirror", self.url, self.type_mask)


class MirrorList(object):
    """
    Managing a list of available mirrors

    .. Note: The use of a Mirror List and different mirrors has been deprecated by
        the developers at `thetvdb.com <http://thetvdb.com>`_ and they will always
        return one and the same mirror information when requested. This functionality
        could and will be removed from future versions of **pytvdbapi**.
    """

    def __init__(self, etree):
        self.data = [
            Mirror(m['id'], m['mirrorpath'], m['typemask'])
            for m in parse_xml(etree, 'Mirror')
        ]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def get_mirror(self, type_mask):
        """
        :param type_mask:
        :return: A :class:`Mirror` object
        :raise: :class:`PytvdbapiError`

        Returns a random :class:`Mirror` object that matches the provided type_mask.
        """
        try:
            return random.choice(
                [m for m in self.data if
                 int(m.type_mask) & int(type_mask) == int(type_mask)])
        except IndexError:
            raise error.PytvdbapiError(u"No Mirror matching {0} found".format(type_mask))
