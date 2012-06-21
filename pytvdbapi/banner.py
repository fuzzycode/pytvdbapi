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
    """
    def __init__(self, mirror, data, show):
        self.mirror, self.data, self.show = mirror, data, show

    def __repr__(self):
        return "<Banner>"

    def __getattr__(self, item):
        if item == "banner_url":
            return self.mirror + "/banners/" + self.BannerPath
        else:
            try:
                return self.data[item]
            except KeyError:
                raise error.TVDBAttributeError(
                    "Banner has no {0} attribute".format(item))
