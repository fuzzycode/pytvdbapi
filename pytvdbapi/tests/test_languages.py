# -*- coding: utf-8 -*-

# Copyright (C) 2013 Björn Larsson

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
from pytvdbapi import api
from types import NoneType


class TestLanguageClass(unittest.TestCase):
    """Test the language class functionality of tvdbapi"""

    def test_creation(self):
        """It should be possible to create a Language instance"""
        l = api.Language("en", "English", 2)
        self.assertTrue(type(l) is not NoneType, "Instance should not be None")

    def test_attributes(self):
        """The language class should have the correct attributes"""

        l = api.Language("en", "English", 2)

        self.assertTrue(hasattr(l, "abbreviation"),
                        "Language class should have abbreviation attribute")
        self.assertTrue(hasattr(l, "name"),
                        "Language class should have name attribute")

    def test_attribute_values(self):
        """Attributes should have the correct values"""
        l = api.Language("en", "English", 2)

        self.assertEquals(l.abbreviation, "en",
                          "Attribute value should be correct")
        self.assertEquals(l.name, "English",
                          "Attribute value should be correct")
        self.assertEquals(l._id, 2,
                          "Attribute value should be correct")


class TestLanguage(unittest.TestCase):
    """Test the language functionality of tvdbapi"""
