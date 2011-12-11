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

#Imports for a more Py3K functionality
from __future__ import absolute_import, print_function


import sys
import unittest
import os

from pytvdbapi import xmlhelpers, language, error
from pytvdbapi.tests import utils, basetest


class TestLanguage(basetest.pytvdbapiTest):
    def setUp(self):
        super(TestLanguage, self).setUp()

        data = utils.file_loader(os.path.join(self.path, "languages.xml"))
        self.languages = language.LanguageList(xmlhelpers.generate_tree(data))

        self.langs = ('da', 'fi', 'nl', 'de', 'it', 'es', 'fr', 'pl', 'hu',
                      'el', 'tr', 'ru', 'he', 'ja', 'pt', 'zh', 'cs', 'sl',
                      'hr', 'ko', 'en', 'sv', 'no')

    def tearDown(self):
        super(TestLanguage, self).tearDown()

    def test_language_list(self):
        """
        It should be able to test if a language exists in the language list
        """

        for l in self.langs:
            self.assertEqual(l in self.languages, True)
            self.assertEqual(self.languages[l].abbreviation, l)

    def test_length_language_list(self):
        """len() should work correctly for a language list"""
        self.assertEqual(len(self.languages), len(self.langs))

    def test_language_representation(self):
        """The __repr__ of a language should function"""
        self.assertEqual(self.languages['sv'].__repr__(),
                          "<Language (Svenska:sv:8)>")

    def test_invalid_languages(self):
        """Function should raise TVDBIndexError when trying to access an
        invalid language"""

        langs = ('pe', 'bz', 'bu')

        for l in langs:
            self.assertRaises(error.TVDBIndexError,
                              self.languages.__getitem__, l)

    def test_iterate_languages(self):
        """It should be able to iterate over the language list"""

        for l in self.languages:
            pass

if __name__ == "__main__":
    sys.exit(unittest.main())
