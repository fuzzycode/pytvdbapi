# -*- coding: utf-8 -*-

# Copyright 2011 Björn Larsson

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

"""A module for actor related functionality."""

__all__ = ['Actor']

from pytvdbapi.error import TVDBAttributeError


class Actor(object):
    """
    Representing an Actor as provided by `thetvdb.com <http://thetvdb.com>`_.
    It Will contain all attributes as delivered from
    `thetvdb.com <http://thetvdb.com>`_, the attributes are described in
    more detail `here <http://www.thetvdb.com/wiki/index.php/API:actors.xml>`_.
    It will also contain the attribute *image_url* that will be the full URL
    to the image of the actor.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56", actors=True)
        >>> show = db.get( 79349, "en" )  # Dexter
        >>> show.update()
        >>> actor = show.actor_objects[0]
        >>> actor
        '<Actor - Michael C. Hall\>'
        >>> actor.Role
        'Dexter Morgan'
        >>> actor.image_url
        'http://thetvdb.com/banners/actors/70947.jpg'
    """
    def __init__(self, mirror, data, show):
        self.mirror, self.data, self.show = mirror, data, show

    def __repr__(self):
        return '<Actor - {0}>'.format(self.Name)

    def __getattr__(self, item):
        if item == 'image_url':
            return self.mirror + "/banners/" + self.Image
        else:
            try:
                return self.data[item]
            except KeyError:
                raise TVDBAttributeError("Actor has no {0} attribute".format(
                    item))

    def __dir__(self):
        return list(self.data.keys()) + ['image_url']
