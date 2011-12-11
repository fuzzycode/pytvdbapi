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

"""
A module for utility functionality.
"""

__all__ = ['merge']


def merge(dict1, dict2, decision=lambda x, y: y):
    """
    :param dict1: First dictionary to merge
    :param dict2: Second dictionary to merge
    :param decision: A callable taking two values v1, v2 returning the value
        to keep. The default is to keep values in dict2.
    :return: A new dictionary with the merged result

    Merging two dictionaries together using *decision* to determine what
    values will be used.
    """
    result = dict(dict1)
    for key, value in list(dict2.items()):
        if key in result:
            result[key] = decision(result[key], value)
        else:
            result[key] = value
    return result
