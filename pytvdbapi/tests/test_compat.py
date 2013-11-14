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

import unittest

from pytvdbapi._compat import implements_to_string, make_unicode, make_bytes, PY2


class TestImplementsString(unittest.TestCase):

    @implements_to_string
    class TestClass(object):
        def __str__(self):
            pass

    def setUp(self):
        self.instance = TestImplementsString.TestClass()

    def test_function_attributes(self):
        """A class with the implements_string decorator, should have the proper function attributes"""

        if PY2:
            self.assertTrue(hasattr(self.instance, '__str__'))
            self.assertTrue(hasattr(self.instance, '__unicode__'))
        else:
            self.assertTrue(hasattr(self.instance, '__str__'))
            self.assertFalse(hasattr(self.instance, '__unicode__'))


class TestMakeUnicode(unittest.TestCase):
    def test_none(self):
        """Passing None should return None"""
        self.assertEqual(make_unicode(None), None)

    def test_non_byte_arguments(self):
        """Passing non byte arguments should return them unchanged"""

        self.assertEqual(type(make_unicode(2)), int)
        self.assertEqual(type(make_unicode(2.2)), float)

    def test_unicode(self):
        """Already encoded strings should be returned unchanged"""
        _input = u"Python 2 String" if PY2 else "Python 3 String"

        self.assertEqual(type(make_unicode(_input)), type(_input))
        self.assertEqual(make_unicode(_input), _input)

    def test_byte_arguments(self):
        """byte arguments should be encoded correctly"""

        if PY2:
            self.assertEqual(type(make_unicode("byte string")), unicode)
        else:
            self.assertEqual(type(make_unicode(b"byte string")), str)


class TestMakeBytes(unittest.TestCase):
    def test_none(self):
        """Passing None should return None"""
        self.assertEqual(None, make_bytes(None))

    def test_bytes(self):
        """Byte types should return bytes"""

        if PY2:
            self.assertEqual(bytes, type(make_bytes(bytes('string'))))
            self.assertEqual(bytes, type(make_bytes(bytearray('string'))))
            self.assertEqual(bytes, type(make_bytes(buffer('string'))))
        else:
            self.assertEqual(bytes, type(make_bytes(bytes('string', 'utf-8'))))
            self.assertEqual(bytes, type(make_bytes(bytearray('string', 'utf-8'))))
            # self.assertEqual(bytes, type(make_bytes(memoryview())))

    def test_non_bytes(self):
        """Non byte types should raise exception"""
        self.assertRaises(TypeError, make_bytes, 2)

    def test_text(self):
        """Text arguments should be encoded properly"""
        _input = u"unicode text" if PY2 else "python 3 string"
        result = make_bytes(_input)

        self.assertEqual(type(result), bytes)
