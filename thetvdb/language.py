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

import logging

from thetvdb.xmlhelpers import parse_xml

__all__ = ['Language', 'LanguageList']

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class Language(object):
    """Holds information about a language instance"""
    def __init__(self, name, abbreviation, id):
        self.name, self.abbreviation, self.id = name, abbreviation, id

    def __repr__(self):
        return "<{0} ({1}:{2}:{3})>".format(
            self.__class__.name, self.name, self.abbreviation, self.id )


class LanguageList(object):
    """Managing a list of language objects"""
    def __init__(self, etree):
        self.data = [
            Language(lang['name'], lang['abbreviation'], lang['id'])
            for lang in  parse_xml( etree, "Language" ) ]

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        return self.data[item]