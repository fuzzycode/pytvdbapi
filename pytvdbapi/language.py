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

"""
A module for managing the languages supported by
`thetvdb.com <http://thetvdb.com>`_
"""

import logging
from collections import Mapping

from pytvdbapi import error
from pytvdbapi.xmlhelpers import parse_xml


__all__ = ['Language', 'LanguageList']

#Module logger object
logger = logging.getLogger(__name__)  # pylint: disable=C0103


class Language(object):
    """Holds information about a language instance"""
    def __init__(self, name, abbreviation, language_id):
        self.name = name
        self.abbreviation = abbreviation
        self.language_id = language_id

    def __repr__(self):
        return "<{0} ({1}:{2}:{3})>".format("Language", self.name,
                                            self.abbreviation,
                                            self.language_id)


class LanguageList(Mapping):
    """Managing a list of language objects"""
    def __init__(self, etree):
        languages = [Language(l['name'], l['abbreviation'], l['id'])
                 for l in parse_xml(etree, "Language")]
        self.data = dict((l.abbreviation, l) for l in languages)

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(list(self.data.items()))

    def __getitem__(self, item):
        """
        :param item: The language abbreviation to fetch
        :return: A :class:`language` object
        :raise: :class:`TVDBIndexError`
        """
        try:
            return self.data[item]
        except KeyError:
            raise error.TVDBIndexError("Item {0} not found".format(item))
