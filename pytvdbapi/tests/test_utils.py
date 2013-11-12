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
import unittest

from pytvdbapi.utils import InsensitiveDictionary


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

    def test_delete(self):
        """It should be possible to delete elements in the dict"""
        d = InsensitiveDictionary()

        d['foo'] = 'baar'
        self.assertTrue('foo' in d, "dict should contain foo")
        self.assertEqual(len(d), 1)

        del (d['foo'])
        self.assertFalse('foo' in d, "dict should not contain foo")
        self.assertEqual(len(d), 0)

    def test_length(self):
        """It should be possible to use the len() method on the dict"""

        d = InsensitiveDictionary()

        self.assertEqual(len(d), 0)

        d['foo'] = 'baar'
        d['baz'] = 2
        self.assertEqual(len(d), 2)

    def test_non_text_keys(self):
        """It should be possible to use non-text keys in insensitive dict"""

        d = InsensitiveDictionary(ignore_case=True)

        d[2] = 'baar'
        self.assertTrue(2 in d)

    def test_clear(self):
        """It should be possible to clear a dict"""
        d = InsensitiveDictionary()

        d['foo'] = 'baar'
        self.assertEqual(len(d), 1)

        d.clear()
        self.assertEqual(len(d), 0)

    def test_keys(self):
        """It should be possible to use the keys() method on the dict"""

        d = InsensitiveDictionary()

        # Create the dict
        keys = ['foo', 'baaz', 'blaa', 2]
        values = ['baar', 'woo', 'blug', 'wow']

        for i in zip(keys, values):
            d[i[0]] = i[1]

        # Test dict
        for k in d.keys():
            self.assertTrue(k in keys)

    def test_values(self):
        """It should be possible to use the values() method on the dict"""

        d = InsensitiveDictionary()

        # Create the dict
        keys = ['foo', 'baaz', 'blaa', 2]
        values = ['baar', 'woo', 'blug', 'wow']

        for i in zip(keys, values):
            d[i[0]] = i[1]

        # Test dict
        for v in d.values():
            self.assertTrue(v in values)

    def test_items(self):
        """It should be possible to use the items() method on the dict"""

        d = InsensitiveDictionary()

        # Create the dict
        keys = ['foo', 'baaz', 'blaa', 2]
        values = ['baar', 'woo', 'blug', 'wow']
        items = zip(keys, values)

        for i in items:
            d[i[0]] = i[1]

        # Test dict
        for i in d.items():
            self.assertTrue(i[0] in keys)
            self.assertTrue(i[1] in values)

    def test_item_iteration(self):
        """It should be possible to iterate over the items in the dict"""
        d = InsensitiveDictionary()

        # Create the dict
        keys = ['foo', 'baaz', 'blaa', 2]
        values = ['baar', 'woo', 'blug', 'wow']
        items = zip(keys, values)

        for i in items:
            d[i[0]] = i[1]

        # Test dict
        for i in d:
            self.assertTrue(i in keys)

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
