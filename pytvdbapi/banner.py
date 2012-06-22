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

"""A module for banner information"""
from pytvdbapi import error


class Banner(object):
    """
    Representing a Banner as provided by `thetvdb.com <http://thetvdb.com>`_.
    It Will contain all attributes as delivered from
    `thetvdb.com <http://thetvdb.com>`_, the attributes are described in
    more detail
    `here <http://www.thetvdb.com/wiki/index.php/API:banners.xml>`_.
    It will also contain the attribute *banner_url* that will be the full URL
    to the image of the banner.
    """
    def __init__(self, mirror, data, show):
        self.mirror, self.data, self.show = mirror, data, show

    def __repr__(self):
        return "<Banner>"

    def __getattr__(self, item):
        if item == "banner_url":
            return self.mirror + "/banners/" + self.BannerPath
        elif item == "Season":  # Season is not always available in XML
            if item in self.data:
                return self.data[item]
            else:
                return ""
        else:
            try:
                return self.data[item]
            except KeyError:
                raise error.TVDBAttributeError(
                    "Banner has no {0} attribute".format(item))

    def __dir__(self):
        attributes = list(self.data.keys()) + ["banner_url"]

        if not "Season" in attributes:
            attributes.append("Season")

        return attributes
