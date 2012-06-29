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

from __future__ import absolute_import, print_function, unicode_literals
import sys
import unittest
import re

from pytvdbapi.api import TVDB
from pytvdbapi import error
from pytvdbapi.actor import Actor


class TestActor(unittest.TestCase):
    def test_get_actors(self):
        """
        The Show instance should have an actor_objects attribute when the
        actor data is loaded.
        """
        api = TVDB("B43FF87DE395DF56", actors=True)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        self.assertEqual(hasattr(show, "actor_objects"), True)

    def test_no_actors(self):
        """
        The Show instance should have an empty actor_objects when the
        actor data has not been loaded.
        """
        api = TVDB("B43FF87DE395DF56", actors=False)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        self.assertEqual(len(show.actor_objects), 0)

    def test_actor_attributes(self):
        """
        The attributes of the Actors class should be correct
        """
        api = TVDB("B43FF87DE395DF56", actors=True)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        actor = show.actor_objects[0]

        self.assertEqual(hasattr(actor, "id"), True)
        self.assertEqual(hasattr(actor, "Image"), True)
        self.assertEqual(hasattr(actor, "Name"), True)
        self.assertEqual(hasattr(actor, "Role"), True)
        self.assertEqual(hasattr(actor, "SortOrder"), True)
        self.assertEqual(hasattr(actor, "image_url"), True)

        self.assertEqual(len(dir(actor)), 6)

    def test_iterable_actors(self):
        """
        It should be possible to iterate over the actor objects
        """
        api = TVDB("B43FF87DE395DF56", actors=True)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        for actor in show.actor_objects:
            self.assertEqual(type(actor), Actor)

    def test_actor_representation(self):
        """
        The representation of the actor should be properly formatted.
        """
        api = TVDB("B43FF87DE395DF56", actors=True)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        regexp = re.compile("^<Actor - .*?>$")

        for actor in show.actor_objects:
            self.assertNotEqual(regexp.match(actor.__repr__()), None)

    def test_invalid_actor_attribute(self):
        """
        Actor instance should raise an exception when accessing an invalid
        attribute.
        """
        api = TVDB("B43FF87DE395DF56", actors=True)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        actor = show.actor_objects[0]
        self.assertRaises(error.TVDBAttributeError, actor.__getattr__, 'foo')

if __name__ == "__main__":
    sys.exit(unittest.main())
