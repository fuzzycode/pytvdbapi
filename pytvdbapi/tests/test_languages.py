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

from __future__ import unicode_literals

import unittest

from pytvdbapi import api

try:
    from types import NoneType
except ImportError:
    # Python >= 3
    NoneType = type(None)


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

    def test_language_list(self):
        """The list of languages should be correct"""
        __languages__ = ["da", "fi", "nl", "de", "it", "es", "fr", "pl",
                         "hu", "el", "tr", "ru", "he", "ja", "pt", "zh",
                         "cs", "sl", "hr", "ko", "en", "sv", "no"]

        ll = api.languages()
        ld = dict((l.abbreviation, l) for l in ll)

        for lang in __languages__:
            self.assertTrue(lang in ld, "{0} should be supported".format(lang))

    def test_language_function(self):
        """It should be possible to obtain the list of supported languages"""

        ll = api.languages()
        self.assertTrue(len(ll) > 0, "Language list should not be empty")
