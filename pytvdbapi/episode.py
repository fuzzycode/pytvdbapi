# -*- coding: utf-8 -*-

# Copyright 2011 - 2014 Björn Larsson

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
Module to manage episode instances.
"""

import logging

from pytvdbapi import error
from pytvdbapi._compat import implements_to_string
from pytvdbapi.utils import InsensitiveDictionary


# Module logger object
logger = logging.getLogger(__name__)


@implements_to_string
class Episode(object):
    """
    :raise: :exc:`pytvdbapi.error.TVDBAttributeError`

    Holds all information about an individual episode. This should be treated
    as a read-only object to obtain the attributes of the episode.

    All episode values returned from thetvdb.com_ are
    accessible as attributes of the episode object.
    TVDBAttributeError will be raised if accessing an invalid attribute. Some
    type conversions of the attributes will take place as follows:

    * Strings of the format yyyy-mm-dd will be converted into a\
        :class:`datetime.date` object.
    * Pipe separated strings will be converted into a list. E.g "foo | bar" =>\
        ["foo", "bar"]
    * Numbers with a decimal point will be converted to float
    * A number will be converted into an int


    It is possible to obtain the containing season through the *Episode.season*
    attribute.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> result = db.search("Dexter", "en")
        >>> show = result[0]
        >>> episode = show[1][2]  # Get episode S01E02

        >>> print(episode.season)
        <Season 001>

        >>> print(episode.EpisodeNumber)
        2

        >>> print(episode.EpisodeName)
        Crocodile

        >>> episode.FirstAired
        datetime.date(2006, 10, 8)

        >>> dir(episode) #doctest: +NORMALIZE_WHITESPACE
        ['Combined_episodenumber',
         'Combined_season', 'DVD_chapter', 'DVD_discid', 'DVD_episodenumber',
         'DVD_season', 'Director', 'EpImgFlag', 'EpisodeName', 'EpisodeNumber',
         'FirstAired', 'GuestStars', 'IMDB_ID', 'Language', 'Overview',
         'ProductionCode', 'Rating', 'RatingCount', 'SeasonNumber', 'Writer',
         'absolute_number', 'filename', 'id', 'lastupdated', 'season',
         'seasonid', 'seriesid', 'thumb_added', 'thumb_height', 'thumb_width']

    .. _thetvdb.com: http://thetvdb.com
    """

    data = {}

    def __init__(self, data, season, config):
        self.season, self.config = season, config
        ignore_case = self.config.get('ignore_case', False)

        self.data = InsensitiveDictionary(ignore_case=ignore_case, **data)  # pylint: disable=W0142

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise error.TVDBAttributeError(u"Episode has no attribute {0}".format(item))

    def __dir__(self):
        attributes = [d for d in list(self.__dict__.keys()) if d not in ('data', 'config')]
        return list(self.data.keys()) + attributes

    def __str__(self):
        return u'<{0} - S{1:03d}E{2:03d}>'.format(
            self.__class__.__name__, self.SeasonNumber, self.EpisodeNumber)

    def __repr__(self):
        return self.__str__()
