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

from __future__ import absolute_import, print_function
from pytvdbapi.utils import InsensitiveDictionary
import unittest


class TestInsensitiveDictionary(unittest.TestCase):
    """Test the insensitive dictionary"""
    def test_create_insensitive_dict(self):
        """
        It should be possible to create a case insensitive dictionary
        """
        d = InsensitiveDictionary(ignore_case=True)

        d['HELLO'] = 'hello'

        self.assertEqual(d['HELLO'], d['hello'])
        self.assertEqual(d['HelLO'], d['HellO'])

        d2 = InsensitiveDictionary([('Test', 'test')], ignore_case=True)
        self.assertEqual(d2['TEST'], d2['test'])

    def test_create_sensitive_dictionary(self):
        """
        It should be possible to create a case sensitive dictionary
        """

        d = InsensitiveDictionary(ignore_case=False)

        d['HELLO'] = 'hello'

        self.assertEqual(d['HELLO'], 'hello')
        self.assertEqual(d['HELLO'], d['HELLO'])
        self.assertRaises(KeyError, d.__getitem__, 'hello')

    def test_get_method(self):
        """
        The dict should support the get method
        """
        d = InsensitiveDictionary(ignore_case=True)

        d['HELLO'] = 'hello'

        self.assertEqual(d.get('HELLO'), d['HELLO'])
        self.assertEqual(d.get('HELLO'), d.get('hello'))

    def test_equality(self):
        """
        The dictionary should support equality tests
        """
        d = InsensitiveDictionary(ignore_case=True)
        d['HELLO'] = 'hello'

        d2 = InsensitiveDictionary(ignore_case=True)
        d2['HELLO'] = 'hello'

        d3 = InsensitiveDictionary(ignore_case=True)
        d3['Foo'] = 'baar'

        self.assertEqual(d == d2, True)
        self.assertEqual(d != d2, False)
        self.assertEqual(d != d3, True)

    def test_contains(self):
        """
        The dictionary should support the "in" syntax
        """
        d = InsensitiveDictionary(ignore_case=True)
        d['HELLO'] = 'hello'

        self.assertEqual('HELLO' in d, True)
        self.assertEqual('hello' in d, True)
        self.assertEqual('HeLlO' in d, True)
        self.assertEqual('foo' in d, False)
