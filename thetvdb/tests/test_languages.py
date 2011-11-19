# -*- coding: utf-8 -*-

# Copyright 2011 Björn Larsson

# This file is part of thetvdb.
#
# thetvdb is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# thetvdb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with thetvdb.  If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase
import sys
import os

from thetvdb import xmlhelpers, language, error
import utils
import basetest


class TestLanguage(basetest.TheTVDBTest):
    def setUp(self):
        super(TestLanguage, self).setUp()

        data = utils.file_loader(os.path.join(self.path, "languages.xml"))
        self.languages = language.LanguageList(xmlhelpers.generate_tree(data))

    def tearDown(self):
        super(TestLanguage, self).tearDown()

    def test_language_list(self):
        """"""