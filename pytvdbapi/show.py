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
Module to manage show instances.
"""

from collections import Sequence
import logging

from pytvdbapi import error
from pytvdbapi._compat import implements_to_string
from pytvdbapi.actor import Actor
from pytvdbapi.banner import Banner
from pytvdbapi.episode import Episode
from pytvdbapi.mirror import TypeMask
from pytvdbapi.season import Season
from pytvdbapi.urls import series, actors, banners
from pytvdbapi.utils import InsensitiveDictionary, merge
from pytvdbapi.xmlhelpers import generate_tree, parse_xml


# Module logger object
logger = logging.getLogger(__name__)

@implements_to_string
class Show(Sequence):
    # pylint: disable=R0902
    """
    :raise: :exc:`pytvdbapi.error.TVDBAttributeError`, :exc:`pytvdbapi.error.TVDBIndexError`

    Holds attributes about a single show and contains all seasons associated
    with a show. The attributes are named exactly as returned from
    thetvdb.com_. This object should be considered a read only container of
    data provided from the server. Some type conversion of of the attributes
    will take place as follows:

    * Strings of the format yyyy-mm-dd will be converted into a\
        :class:`datetime.date` object.
    * Pipe separated strings will be converted into a list. E.g "foo | bar" =>\
        ["foo", "bar"]
    * Numbers with a decimal point will be converted to float
    * A number will be converted into an int


    The Show uses lazy evaluation and will only load the full data set from
    the server when this data is needed. This is to speed up the searches and
    to reduce the workload of the servers. This way,
    data will only be loaded when actually needed.

    The Show supports iteration to iterate over the Seasons contained in the
    Show. You can also index individual seasons with the [ ] syntax.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> result = db.search("dexter", "en")
        >>> show = result[0]

        >>> dir(show)  # List the set of basic attributes # doctest: +NORMALIZE_WHITESPACE
        ['AliasNames', 'FirstAired', 'IMDB_ID', 'Network',
         'Overview', 'SeriesName', 'actor_objects', 'api',
         'banner', 'banner_objects', 'id', 'lang', 'language',
         'seriesid', 'zap2it_id']

        >>> show.update()  # Load the full data set from the server
        >>> dir(show)  # List the full set of attributes # doctest: +NORMALIZE_WHITESPACE
        ['Actors', 'Airs_DayOfWeek', 'Airs_Time', 'AliasNames',
         'ContentRating', 'FirstAired', 'Genre', 'IMDB_ID', 'Language',
         'Network', 'NetworkID', 'Overview', 'Rating', 'RatingCount', 'Runtime',
         'SeriesID', 'SeriesName', 'Status', 'actor_objects', 'added', 'addedBy',
         'api', 'banner', 'banner_objects', 'fanart', 'id', 'lang', 'language',
         'lastupdated', 'poster', 'seriesid', 'tms_wanted_old', 'zap2it_id']

    .. note:: When searching, thetvdb.com_ provides a basic set of attributes
        for the show. When the full data set is loaded thetvdb.com_ provides a
        complete set of attributes for the show. The full data set is loaded
        when accessing the season data of the show. If you need access to the
        full set of attributes you can force the loading of the full data set
        by calling the :func:`update()` function.

    .. _thetvdb.com: http://thetvdb.com
    """

    data = {}

    def __init__(self, data, api, language, config, full_data=None):
        self.api, self.lang, self.config = api, language, config
        self.seasons = dict()

        self.ignore_case = self.config.get('ignore_case', False)
        self.data = InsensitiveDictionary(ignore_case=self.ignore_case, **data)  # pylint: disable=W0142

        self.data['actor_objects'] = list()
        self.data['banner_objects'] = list()

        if full_data is not None:
            self._populate_data(full_data)

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise error.TVDBAttributeError(u"Show has no attribute named {0}".format(item))

    def __dir__(self):
        attributes = [d for d in list(self.__dict__.keys())
                      if d not in ('data', 'config', 'ignore_case', 'seasons')]
        return list(self.data.keys()) + attributes

    def __iter__(self):
        if not self.seasons:
            self._populate_data()

        return iter(sorted(list(self.seasons.values()), key=lambda season: season.season_number))

    def __len__(self):
        if not len(self.seasons):
            self._populate_data()

        return len(self.seasons)

    def __reversed__(self):
        for i in sorted(self.seasons.keys(), reverse=True):
            yield self[i]

    def __getitem__(self, item):
        if len(self.seasons) == 0:
            self._populate_data()

        if isinstance(item, int):
            try:
                return self.seasons[item]
            except KeyError:
                raise error.TVDBIndexError(u"Season {0} not found".format(item))

        elif isinstance(item, slice):
            indices = sorted(self.seasons.keys())[item]  # Slice the keys
            return [self[i] for i in indices]
        else:
            raise error.TVDBValueError(u"Index should be an integer or slice")

    def __str__(self):
        return u'<{0} - {1}>'.format(self.__class__.__name__, self.SeriesName)

    def __repr__(self):
        return self.__str__()

    def update(self):
        """
        Updates the data structure with data from the server.
        """
        self._populate_data()

    def _populate_data(self, data=None):
        """
        Populates the Show object with data. This will hit the network to
        download the XML data from `thetvdb.com <http://thetvdb.com>`_.
        :class:`Season` and `:class:Episode` objects will be created and
        added as needed.

        .. Note: This function is not intended to be used by clients of the
        API and should only be used internally by the Show class to manage its
        structure.
        """
        logger.debug(u"Populating season data from URL.")

        if data is None:
            context = {'mirror': self.api.mirrors.get_mirror(TypeMask.XML).url,
                       'api_key': self.config['api_key'],
                       'seriesid': self.id,
                       'language': self.lang}
            url = series.format(**context)
            data = self.api.loader.load(url)
            data = generate_tree(data)

        episodes = [d for d in parse_xml(data, "Episode")]

        show_data = parse_xml(data, "Series")
        assert len(show_data) == 1, u"Should only have 1 Show section"

        self.data = merge(self.data, InsensitiveDictionary(show_data[0], ignore_case=self.ignore_case))

        for episode_data in episodes:
            season_nr = int(episode_data['SeasonNumber'])
            if season_nr not in self.seasons:
                self.seasons[season_nr] = Season(season_nr, self)

            episode = Episode(episode_data, self.seasons[season_nr], self.config)
            self.seasons[season_nr].append(episode)

        # If requested, load the extra actors data
        if self.config.get('actors', False):
            self.load_actors()

        # if requested, load the extra banners data
        if self.config.get('banners', False):
            self.load_banners()

    def load_actors(self):
        """
        .. versionadded:: 0.4

        Loads the extended actor information into a list of :class:`pytvdbapi.actor.Actor` objects.
        They are available through the *actor_objects* attribute of the show.

        If you have used the `actors=True` keyword when creating the :class:`TVDB` instance
        the actors will be loaded automatically and there is no need to use this
        function.

        .. seealso::
          :class:`TVDB` for information on how to use the *actors* keyword
          argument.
        """
        context = {'mirror': self.api.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key'],
                   'seriesid': self.id}
        url = actors.format(**context)

        logger.debug(u'Loading Actors data from {0}'.format(url))

        data = generate_tree(self.api.loader.load(url))

        mirror = self.api.mirrors.get_mirror(TypeMask.BANNER).url

        # generate all the Actor objects
        # pylint: disable=W0201
        self.actor_objects = [Actor(mirror, d, self)
                              for d in parse_xml(data, 'Actor')]

    def load_banners(self):
        """
        .. versionadded:: 0.4

        Loads the extended banner information into a list of :class:`pytvdbapi.banner.Banner` objects.
        They are available through the *banner_objects* attribute of the show.

        If you have used the `banners=True` keyword when creating the :class:`TVDB` instance the
        banners will be loaded automatically and there is no need to use this
        function.

        .. seealso::
          :class:`TVDB` for information on how to use the *banners* keyword
          argument.
        """
        context = {'mirror': self.api.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key'],
                   'seriesid': self.id}

        url = banners.format(**context)
        logger.debug(u'Loading Banner data from {0}'.format(url))

        data = generate_tree(self.api.loader.load(url))
        mirror = self.api.mirrors.get_mirror(TypeMask.BANNER).url

        # pylint: disable=W0201
        self.banner_objects = [Banner(mirror, b, self) for b in parse_xml(data, "Banner")]

    def find(self, key):
        """
        .. versionadded:: 0.5

        :param key:
        :returns: An :class:`Episode` instance or None

        Finds the first :class:`Episode` for witch :code:`key` returns :code:`True`.

        .. note::
            The order in which the :class:`Episode` instances are searched is not guaranteed and the first
            match found is not necessarily the first one in a chronological sense.

        .. seealso:: :func:`Season.find` for information on finding an episode in a specific season
        """
        for season in self:
            episode = season.find(key=key)
            if episode is not None:
                return episode
        return None

    def filter(self, key):
        """
        .. versionadded:: 0.5

        :param key:
        :returns: A list of 0 or more :class:`Episode` instances

        Finds all :class:`Episode` instances for witch :code:`key` returns :code:`True`.

        .. seealso:: :func:`Season.filter` for information on filtering episodes in a specific season
        """
        result = list()
        for season in self:
            result.extend(season.filter(key=key))
        return result
