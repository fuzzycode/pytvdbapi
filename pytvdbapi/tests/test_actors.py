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

from __future__ import absolute_import, print_function, unicode_literals
import sys
import unittest

from pytvdbapi.api import TVDB
from pytvdbapi import error
from pytvdbapi.actor import Actor


class TestActor(unittest.TestCase):
    def setUp(self):
        api = TVDB("B43FF87DE395DF56", actors=True)
        self.show = api.get_series(79349, "en")  # Load the series Dexter
        self.show.update()

    def test_get_actors(self):
        """
        The Show instance should have an actor_objects attribute when the
        actor data is loaded.
        """

        self.assertEqual(hasattr(self.show, "actor_objects"), True)

    def test_no_actors(self):
        """
        The Show instance should have an empty actor_objects when the
        actor data has not been loaded.
        """
        api = TVDB("B43FF87DE395DF56", actors=False)
        show = api.get_series(79349, "en")  # Load the series Dexter
        show.update()

        self.assertEqual(len(show.actor_objects), 0)

    def test_actor_attributes(self):
        """
        The attributes of the Actors class should be correct
        """
        actor = self.show.actor_objects[0]

        self.assertEqual(hasattr(actor, "id"), True)
        self.assertEqual(hasattr(actor, "Image"), True)
        self.assertEqual(hasattr(actor, "Name"), True)
        self.assertEqual(hasattr(actor, "Role"), True)
        self.assertEqual(hasattr(actor, "SortOrder"), True)
        self.assertEqual(hasattr(actor, "image_url"), True)

    def test_insensitive_attributes(self):
        """If selected, it should be possible to access the attributes in a case insensitive manner"""

        api = TVDB("B43FF87DE395DF56", actors=True, ignore_case=True)
        show = api.get_series(79349, "en")  # Load the series Dexter
        show.update()

        actor = show.actor_objects[0]
        for a in dir(actor):
            self.assertTrue(hasattr(actor, a))
            self.assertTrue(hasattr(actor, a.lower()))
            self.assertTrue(hasattr(actor, a.upper()))

    def test_iterable_actors(self):
        """
        It should be possible to iterate over the actor objects
        """

        for actor in self.show.actor_objects:
            self.assertEqual(type(actor), Actor)

    def test_invalid_actor_attribute(self):
        """
        Actor instance should raise an exception when accessing an invalid
        attribute.
        """

        actor = self.show.actor_objects[0]
        self.assertRaises(error.TVDBAttributeError, actor.__getattr__, 'foo')

    def test_unicode_attributes(self):
        """The attributes should be unicode on Python 2.X and str on Python 3.X"""
        _type = unicode if sys.version < '3' else str

        actor = self.show.actor_objects[0]

        for attr_name in dir(actor):
            attr = getattr(actor, attr_name)
            if type(attr) not in (float, int):
                if type(attr) in (list,):
                    for a in attr:
                        self.assertEqual(type(a), _type)
                else:
                    self.assertEqual(type(attr), _type)

    def test_actor_repr(self):
        """Actor objects should have a __repr__ attribute and it should be callable"""

        actor = self.show.actor_objects[2]

        self.assertTrue(hasattr(actor, '__repr__'))
        self.assertTrue(hasattr(actor, '__str__'))

        repr(actor)

    def test_actor_pickled(self):
        """It should be possible to pickle an actor object"""

        import pickle

        actor = self.show.actor_objects[5]

        pickled_actor = pickle.dumps(actor)
        loaded_actor = pickle.loads(pickled_actor)

        self.assertEqual(actor.Name, loaded_actor.Name)

if __name__ == "__main__":
    sys.exit(unittest.main())
