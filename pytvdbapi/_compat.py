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
A compatibility module for easing the development for Python 2.X and 3.X
with a shared code base. Strongly inspired/copied by the approach taken by werkzeug.
"""

# Exclude the whole file from style testing
# flake8: noqa
# pylint: skip-file

import sys

__all__ = ['implements_to_string', 'make_unicode', 'make_bytes', 'text_type', 'string_types']

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

__identity = lambda x: x

if PY2:
    text_type = unicode
    string_types = (str, unicode)
    int_types = (int, long)

    def implements_to_string(cls):
        """
        Decorator used on classes implementing the __str__ function

        The __str__ function will be changed to __unicode__
        and the "standard" __str__ implemented in terms of __unicode__ is added
        """
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

    def make_unicode(data, encoding='utf-8', error='strict'):
        """
        :param data:
        :param encoding:
        :param error:

        Turn a string into unicode data, non strings are returned unchanged
        """
        if isinstance(data, str):
            try:
                return unicode(data, encoding=encoding, errors=error)
            except UnicodeDecodeError:
                return data
        else:
            return data

    def make_bytes(data, encoding='utf-8', error='strict'):
        """
        :param data:
        :param encoding:
        :param error:

        Turn unicode data into bytes
        """
        if data is None:
            return None
        if isinstance(data, (bytes, bytearray, buffer)):
            return bytes(data)
        if isinstance(data, unicode):
            return data.encode(encoding, error)
        raise TypeError('Expected bytes')

else:  # Python 3 implementation
    text_type = str
    string_types = (str, )
    int_types = (int, )
    implements_to_string = __identity

    def make_unicode(data, encoding='utf-8', error='strict'):
        """"""
        if isinstance(data, bytes):
            return data.decode(encoding, error)
        return data

    def make_bytes(data, encoding='utf-8', error='strict'):
        """
        :param data:
        :param encoding:
        :param error:

        Turn unicode data into bytes
        """
        if data is None:
            return None
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        if isinstance(data, str):
            return data.encode(encoding, error)
        raise TypeError('Expected bytes')
