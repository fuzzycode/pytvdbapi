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

# pylint: disable=R0922

"""
A module for utility functionality.
"""

from functools import wraps
from collections import MutableMapping

from pytvdbapi._compat import make_unicode, int_types


__all__ = ['unicode_arguments', 'deprecate_episode_id', 'TransformedDictionary', 'InsensitiveDictionary']


def unicode_arguments(func):
    """
    :param func: The function to wrap
    :type func: A function object

    A wrapper to convert all text arguments into unicode objects.
    """

    @wraps(func)
    def __wrapper__(*args, **kwargs):
        args = [make_unicode(arg) for arg in args]
        kwargs = dict((k, make_unicode(v)) for (k, v) in kwargs.items())
        return func(*args, **kwargs)

    return __wrapper__


def deprecate_episode_id(func):
    """
    Utility function to help deprecating the episode_id parameter without loosing backward compatibility.

    :param func: The function to wrap
    :type func: A function object
    """
    @wraps(func)
    def __wrapper__(*args, **kwargs):
        args = list(args)

        # Check if the first argument is an int, and assume that it was the episode id
        if isinstance(args[1], int_types):
            episodeid = args[1]
            if 'episodeid' not in kwargs:
                kwargs['episodeid'] = episodeid

            del args[1]

        return func(*args, **kwargs)
    return __wrapper__


class TransformedDictionary(MutableMapping, object):
    """
    An abstract dictionary base class that support transformation
    of the key used for storing.
    """

    def __transform__(self, key):
        raise NotImplementedError("Not implemented")

    def __init__(self, *args, **kwargs):
        self._data = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, item):
        return self._data[self.__transform__(item)]

    def __setitem__(self, key, value):
        self._data[self.__transform__(key)] = value

    def __delitem__(self, key):
        del self._data[self.__transform__(key)]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        """
        :return: A list of dictionary keys
        """
        return self._data.keys()

    def clear(self):
        """
        Clear the dictionary content, making its length 0
        """
        self._data.clear()

    def items(self):
        """
        :return: A list of all items in the dictionary
        """
        return self._data.items()

    def values(self):
        """
        :return: A list of the values in the dictionary
        """
        return self._data.values()


class InsensitiveDictionary(TransformedDictionary):
    """
    A dictionary supporting the use of case insensitive keys
    """

    def __init__(self, *args, **kwargs):
        self.ignore_case = kwargs.pop('ignore_case', False)
        super(InsensitiveDictionary, self).__init__(*args, **kwargs)

    def __transform__(self, key):
        if self.ignore_case:
            try:
                return key.lower()
            except AttributeError:
                return key
        else:
            return key
