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

"""
A small, clean and easy to use API for the thetvdb.com online DB service. It
is designed to be fast, easy to use and to respect the functionality of the
thetvdb.com API.

This module is the public interface for the package.

Basic usage::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56")
    >>> search = db.search("How I met your mother", "en")
    >>> show = search[0]
    >>> show.SeriesName
    'How I Met Your Mother'
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import tempfile
import sys
import os
from collections import Mapping, namedtuple

# pylint: disable=E0611, F0401, W0622
from pytvdbapi.actor import Actor
from pytvdbapi.banner import Banner
from pytvdbapi.utils import InsensitiveDictionary


try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
    # pylint: enable=E0611, F0401

from pytvdbapi import error
from pytvdbapi.__init__ import __NAME__ as name
from pytvdbapi.loader import Loader
from pytvdbapi.mirror import MirrorList, TypeMask
from pytvdbapi.utils import merge
from pytvdbapi.xmlhelpers import parse_xml, generate_tree

# URL templates used for loading the data from thetvdb.com
__mirrors__ = "http://www.thetvdb.com/api/{api_key}/mirrors.xml"
__time__ = "http://www.thetvdb.com/api/Updates.php?type=none"
__search__ = "http://www.thetvdb.com/api/GetSeries.php?seriesname={series}&language={language}"
__series__ = "{mirror}/api/{api_key}/series/{seriesid}/all/{language}.xml"
__episode__ = "{mirror}/api/{api_key}/episodes/{episodeid}/{language}.xml"
__actors__ = "{mirror}/api/{api_key}/series/{seriesid}/actors.xml"
__banners__ = "{mirror}/api/{api_key}/series/{seriesid}/banners.xml"


__all__ = ['Episode', 'Season', 'Show', 'Search', 'TVDB']

# Module logger object
logger = logging.getLogger(__name__)

__Language = namedtuple("__Language", ['abbrev', 'name', 'id'])

__LANGUAGES__ = {"da": __Language(abbrev="da", name="Dansk", id=10),
                 "fi": __Language(abbrev="fi", name="Suomeksi", id=11),
                 "nl": __Language(abbrev="nl", name="Nederlands", id=13),
                 "de": __Language(abbrev="de", name="Deutsch", id=14),
                 "it": __Language(abbrev="it", name="Italiano", id=15),
                 "es": __Language(abbrev="es", name="Español", id=16),
                 "fr": __Language(abbrev="fr", name="Français", id=17),
                 "pl": __Language(abbrev="pl", name="Polski", id=18),
                 "hu": __Language(abbrev="hu", name="Magyar", id=19),
                 "el": __Language(abbrev="el", name="Ελληνικά", id=20),
                 "tr": __Language(abbrev="tr", name="Türkçe", id=21),
                 "ru": __Language(abbrev="ru", name="русский язык", id=22),
                 "he": __Language(abbrev="he", name=" עברית", id=24),
                 "ja": __Language(abbrev="ja", name="日本語", id=25),
                 "pt": __Language(abbrev="pt", name="Português", id=26),
                 "zh": __Language(abbrev="zh", name="中文", id=27),
                 "cs": __Language(abbrev="cs", name="čeština", id=28),
                 "sl": __Language(abbrev="sl", name="Slovenski", id=30),
                 "hr": __Language(abbrev="hr", name="Hrvatski", id=31),
                 "ko": __Language(abbrev="ko", name="한국어", id=32),
                 "en": __Language(abbrev="en", name="English", id=7),
                 "sv": __Language(abbrev="sv", name="Svenska", id=8),
                 "no": __Language(abbrev="no", name="Norsk", id=9)}


class Episode(object):
    """
    :raise: :class:`pytvdbapi.error.TVDBAttributeError`

    Holds all information about an individual episode. This should be treated
    as a read-only object to obtain the attributes of the episode.

    All episode values returned from thetvdb.com_ are
    accessible as attributes of the episode object. The attributes will be
    named exactly as returned from thetvdb.com_ and are case sensitive.
    TVDBAttributeError will be raised if accessing an invalid attribute. Some
    type conversions of the attributes will take place as follows:

    * Strings of the format yyyy-mm-dd will be converted into a\
        :class:`datetime.date` object.
    * Pipe separated strings will be converted into a list. E.g "foo | bar" =>\
        ["foo", "bar"]
    * Numbers with a decimal point will be converted to float
    * A number will be converted into an int


    It is possible to obtain the containing season through the Episode.season
    attribute.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> show = search[0]
        >>> episode = show[1][5]

        >>> dir(episode) #doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
        ['Combined_episodenumber', 'Combined_season', 'DVD_chapter',
        'DVD_discid', 'DVD_episodenumber', 'DVD_season', 'Director',
        'EpImgFlag', 'EpisodeName', 'EpisodeNumber', 'FirstAired',
        'GuestStars', 'IMDB_ID', '__Language', 'Overview', 'ProductionCode',
        'Rating', 'RatingCount', 'SeasonNumber', 'Writer', 'absolute_number',
        'filename', 'id', 'lastupdated', 'season', 'seasonid', 'seriesid',
        ...]

        >>> episode.EpisodeName
        'Love American Style'

        >>> episode.GuestStars #doctest: +NORMALIZE_WHITESPACE
        ['Terry Woodberry', 'Carmen Olivares', 'Ashley Rose Orr',
        'Demetrius Grosse', 'Monique Curnen', 'June Angela',
        'Valerie Dillman', 'Brad Henke', 'Jose Zuniga', 'Allysa Tacher',
        'Lizette Carrion', 'Norma Fontana', 'Minerva Garcia',
        'Josh Daugherty', 'Geoffrey Rivas']

        >>> episode.FirstAired
        datetime.date(2006, 10, 29)

        >>> episode.season
        <Season 001>

    .. _thetvdb.com: http://thetvdb.com
    """
    def __init__(self, data, season, config):
        self.season, self.config = season, config
        ignore_case = self.config.get('ignore_case', False)

        self.data = InsensitiveDictionary(ignore_case=ignore_case, **data)  # pylint: disable=W0142

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            logger.error("Episode has no attribute {0}".format(item))
            raise error.TVDBAttributeError("Episode has no attribute {0}".format(item))

    def __dir__(self):
        attributes = [d for d in list(self.__dict__.keys()) if d not in ('data', 'config')]
        return list(self.data.keys()) + attributes

    def __repr__(self):
        try:
            return "<Episode S{0:03d}E{1:03d} - {2}>".format(int(self.SeasonNumber),
                                                             int(self.EpisodeNumber),
                                                             self.EpisodeName)
        except error.TVDBAttributeError:
            return "<Episode>"


class Season(Mapping):
    # pylint: disable=R0924
    """
    :raise: :class:`pytvdbapi.error.TVDBIndexError`

    Holds all the episodes that belong to a specific season. It is possible
    to iterate over the Season to obtain the individual :class:`Episode`
    instances. It is also possible to obtain an individual episode using the
    [ ] syntax. It will raise :class:`pytvdbapi.error.TVDBIndexError` if trying to index
    an invalid episode index.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> show = search[0]
        >>> season = show[1]
        >>> len(season)
        12
        >>> season[3]
        <Episode S001E003 - Popping Cherry>
        >>> for episode in season:
        ...     print(episode)
        ...
        <Episode S001E001 - Dexter>
        <Episode S001E002 - Crocodile>
        <Episode S001E003 - Popping Cherry>
        <Episode S001E004 - Let's Give the Boy a Hand>
        <Episode S001E005 - Love American Style>
        <Episode S001E006 - Return to Sender>
        <Episode S001E007 - Circle of Friends>
        <Episode S001E008 - Shrink Wrap>
        <Episode S001E009 - Father Knows Best>
        <Episode S001E010 - Seeing Red>
        <Episode S001E011 - Truth Be Told>
        <Episode S001E012 - Born Free>
    """

    def __init__(self, season_number, show):
        self.show, self.season_number = show, season_number
        self.episodes = dict()

    def __getitem__(self, item):
        try:
            return self.episodes[item]
        except KeyError:
            logger.error("Episode {0} not found".format(item))
            raise error.TVDBIndexError("Index {0} not found".format(item))

    def __len__(self):
        return len(self.episodes)

    def __iter__(self):
        return iter(sorted(list(self.episodes.values()), key=lambda ep: ep.EpisodeNumber))

    def __repr__(self):
        return "<Season {0:03}>".format(self.season_number)

    def append(self, episode):
        """
        :param episode: The episode to append
        :type episode: :class:`Episode`

        Adds a new :class:`Episode` to the season. If an episode with the same
        EpisodeNumber already exists, it will be overwritten.
        """
        assert type(episode) in (Episode,)
        logger.debug("{0} adding episode {1}".format(self, episode))

        self.episodes[int(episode.EpisodeNumber)] = episode


class Show(Mapping):
    # pylint: disable=R0924, R0902
    """
    :raise: :class:`pytvdbapi.error.TVDBAttributeError`, :class:`pytvdbapi.error.TVDBIndexError`

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

    .. note:: When searching, thetvdb.com_ provides a basic set of attributes
        for the show. When the full data set is loaded thetvdb.com_ provides a
        complete set of attributes for the show. The full data set is loaded
        when accessing the season data of the show. If you need access to the
        full set of attributes you can force the loading of the full data set
        by calling the :func:`update()` function.


    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> show = search[0]
        >>> dir(show) #doctest: +NORMALIZE_WHITESPACE
        ['AliasNames', 'FirstAired', 'IMDB_ID', 'Network', 'Overview',
          'SeriesName', 'actor_objects', 'api', 'banner', 'banner_objects',
           'id', 'lang', 'language', 'seasons', 'seriesid', 'zap2it_id']

        >>> show.update()

        >>> dir(show) #doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
        ['Actors', 'Airs_DayOfWeek', 'Airs_Time', 'AliasNames',
         'ContentRating', 'FirstAired', 'Genre', 'IMDB_ID',
        '__Language', 'Network', 'NetworkID', 'Overview', 'Rating',
         'RatingCount', 'Runtime', 'SeriesID', 'SeriesName',
        'Status', 'actor_objects', 'added', 'addedBy', 'api',
         'banner', 'banner_objects', 'fanart', 'id', 'lang',
        'language', 'lastupdated', 'poster', 'seasons', 'seriesid',
         ...]

        >>> len(show)
        9

       >>> show[5]
       <Season 005>

        >>> for season in show:
        ...     print(season)
        ...
        <Season 000>
        <Season 001>
        <Season 002>
        <Season 003>
        <Season 004>
        <Season 005>
        <Season 006>
        <Season 007>
        <Season 008>


    .. _thetvdb.com: http://thetvdb.com
    """
    def __init__(self, data, api, language, config):
        self.api, self.lang, self.config = api, language, config
        self.seasons = dict()

        self.actor_objects = list()
        self.banner_objects = list()

        self.ignore_case = self.config.get('ignore_case', False)
        self.data = InsensitiveDictionary(ignore_case=self.ignore_case, **data)  # pylint: disable=W0142

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise error.TVDBAttributeError("Show has no attribute named {0}".format(item))

    def __repr__(self):
        return "<Show - {0}>".format(self.SeriesName)

    def __dir__(self):
        attributes = [d for d in list(self.__dict__.keys()) if d not in ('data', 'config', 'ignore_case')]
        return list(self.data.keys()) + attributes

    def __iter__(self):
        if not self.seasons:
            self._populate_data()

        return iter(sorted(list(self.seasons.values()), key=lambda season: season.season_number))

    def __len__(self):
        if not len(self.seasons):
            self._populate_data()

        return len(self.seasons)

    def __getitem__(self, item):
        if not item in self.seasons:
            self._populate_data()

        try:
            return self.seasons[item]
        except KeyError:
            raise error.TVDBIndexError("Season {0} not found".format(item))

    def update(self):
        """
        Updates the data structure with data from the server.
        """
        self._populate_data()

    def _populate_data(self):
        """
        Populates the Show object with data. This will hit the network to
        downlaod the XML data from `thetvdb.com <http://thetvdb.com>`_.
        :class:`Season` and `:class:Episode` objects will be created and
        added as needed.

        .. Note: This function is not intended to be used by clients of the
        API and should only be used internally by the Show class to manage its
        structure.
        """
        logger.debug("Populating season data from URL.")

        context = {'mirror': self.api.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key'],
                   'seriesid': self.id,
                   'language': self.lang}

        url = __series__.format(**context)
        data = generate_tree(self.api.loader.load(url))
        episodes = [d for d in parse_xml(data, "Episode")]

        show_data = parse_xml(data, "Series")
        assert len(show_data) == 1, "Should only have 1 Show section"

        self.data = merge(self.data, InsensitiveDictionary(show_data[0], ignore_case=self.ignore_case))

        for episode_data in episodes:
            season_nr = int(episode_data['SeasonNumber'])
            if not season_nr in self.seasons:
                self.seasons[season_nr] = Season(season_nr, self)

            episode = Episode(episode_data, self.seasons[season_nr], self.config)
            self.seasons[season_nr].append(episode)

        #If requested, load the extra actors data
        if self.config.get('actors', False):
            self._load_actors()

        #if requested, load the extra banners data
        if self.config.get('banners', False):
            self._load_banners()

    def _load_actors(self):
        """
        Loads the extended Actor data from `thetvdb.com <http://thetvdb.com>`_
        and adds this to the actor_objects attribute.

        .. Note: This function is not intended to be used by clients of the
            API and should only be used internally by the Show class to
            manage its structure.
        """
        context = {'mirror': self.api.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key'],
                   'seriesid': self.id}
        url = __actors__.format(**context)

        logger.debug('Loading Actors data from {0}'.format(url))

        data = generate_tree(self.api.loader.load(url))

        mirror = self.api.mirrors.get_mirror(TypeMask.BANNER).url

        #generate all the Actor objects
        self.actor_objects = [Actor(mirror, d, self)
                              for d in parse_xml(data, 'Actor')]

    def _load_banners(self):
        """
        Loads the extended Banner data from `thetvdb.com <http://thetvdb.com>`_
        and adds this to the banner_objects attribute.

        .. Note: This function is not intended to be used by clients of the
            API and should only be used internally by the Show class to
            manage its structure.
        """
        context = {'mirror': self.api.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key'],
                   'seriesid': self.id}

        url = __banners__.format(**context)
        logger.debug('Loading Banner data from {0}'.format(url))

        data = generate_tree(self.api.loader.load(url))
        mirror = self.api.mirrors.get_mirror(TypeMask.BANNER).url

        self.banner_objects = [Banner(mirror, b, self) for b in parse_xml(data, "Banner")]


class Search(object):
    # pylint: disable=R0924
    """

    :raise: :class:`pytvdbapi.error.TVDBIndexError`

    A search result returned from calling :func:`TVDB.search()`. It supports
    iterating over the results, and the individual shows matching the search
    can be accessed using the [ ] syntax.

    The search will contain 0 or more :class:`Show()` instances matching the
    search.

    The shows will be stored in the same order as they are returned from
    `thetvdb.com <http://thetvdb.com>`_. They state that if there is a
    perfect match to the search, it will be the first element returned.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> for s in search:
        ...     print(s)
        ...
        <Show - Dexter>
    """

    def __init__(self, result, search, language):
        self.result, self.search, self.language = result, search, language

    def __len__(self):
        return len(self.result)

    def __getitem__(self, item):
        try:
            return self.result[item]
        except (IndexError, TypeError):
            raise error.TVDBIndexError("Index out of range ({0})".format(item))

    def __iter__(self):
        return iter(self.result)


class TVDB(object):
    """
    :param api_key: The API key to use to communicate with the server
    :param kwargs:

    This is the main entry point for the API. The functionality of the API is
    controlled by configuring the key word arguments. The supported key word
    arguments are:

    * *force_lang* (default=False).

    * *cache_dir* (default=/<system tmp dir>/pytvdbapi/). Specifies the
      directory to use for caching the server requests.

    .. versionadded:: 0.3

    * *actors* (default=False) The extended actor information is stored in a
      separate XML file and would require an additional request to the server
      to obtain. To limit the resource usage, the actor information will only
      be loaded when explicitly requested.

      .. note:: The :class:`Show()` object always contain a list of actor
        names.

    * *banners* (default=False) The extended banner information is stored in a
      separate XML file and would require an additional request to the server
      to obtain. To limit the resource usage, the banner information will only
      be loaded when explicitly requested.

    .. versionadded:: 0.4

    * *ignore_case* (default=False) If set to True, all attributes on the :class:`Show` and
      :class:`Episode` instances will be accessible in a case insensitive manner. If set to
      False, the default, all attributes will be case sensitive and retain the same casing
      as provided by `thetvdb.com <http://thetvdb.com>`_.


    """

    def __init__(self, api_key, **kwargs):
        self.config = dict()

        #cache old searches to avoid hitting the server
        self.search_buffer = dict()

        #Store the path to where we are
        self.path = os.path.abspath(os.path.dirname(__file__))

        #extract all argument and store for later use
        self.config['api_key'] = api_key
        self.config['cache_dir'] = kwargs.get("cache_dir", os.path.join(tempfile.gettempdir(), name))
        self.config['actors'] = kwargs.get('actors', False)
        self.config['banners'] = kwargs.get('banners', False)
        self.config['ignore_case'] = kwargs.get('ignore_case', False)

        #Create the loader object to use
        self.loader = Loader(self.config['cache_dir'])

        #Create the list of available mirrors
        tree = generate_tree(self.loader.load(__mirrors__.format(**self.config)))
        self.mirrors = MirrorList(tree)

    def search(self, show, language, cache=True):
        """
        :param show: The show name to search for
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
            resources will be reloaded from server.
        :return: A :class:`Search()` instance
        :raise: :class:`pytvdbapi.error.TVDBValueError`

        Searches the server for a show with the provided show name in the
        provided language. The language should be one of the supported
        language abbreviations or it could be set to *all* to search all
        languages. It will raise :class:`pytvdbapi.error.TVDBValueError` if
        an invalid language is provided.

        Searches are always cached within a session to make subsequent
        searches with the same parameters really cheap and fast. If *cache*
        is set to True searches will also be cached across sessions,
        this is recommended to increase speed and to reduce the workload of
        the servers.

        Example::

            >>> from pytvdbapi import api
            >>> db = api.TVDB("B43FF87DE395DF56")
            >>> search = db.search("Dexter", "en")
            >>> for s in search:
            ...     print(s)
            ...
            <Show - Dexter>
        """
        logger.debug("Searching for {0} using language {1}".format(show, language))

        if language != 'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError("{0} is not a valid language".format(language))

        if (show, language) not in self.search_buffer or not cache:
            if sys.version_info < (3, 0):
                show = str(show.encode('utf-8'))

            context = {'series': quote(show), "language": language}
            data = generate_tree(self.loader.load(__search__.format(**context), cache))
            shows = [Show(d, self, language, self.config) for d in parse_xml(data, "Series")]

            self.search_buffer[(show, language)] = shows

        return Search(self.search_buffer[(show, language)], show, language)

    def get(self, series_id, language, cache=True):
        """
        .. versionadded:: 0.3

        :param series_id: The Show Id to fetch
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
                    resources will be reloaded from server.

        :return: A :class:`Show()` instance
        :raise: :class:`pytvdbapi.error.TVDBValueError`, :class:`pytvdbapi.error.TVDBIdError`

        Provided a valid Show ID, the data for the show is fetched and a
        corresponding :class:`Show()` object is returned.

        Example::

            >>> from pytvdbapi import api
            >>> db = api.TVDB("B43FF87DE395DF56")
            >>> show = db.get( 79349, "en" )
            >>> show.id
            79349
            >>> show.SeriesName
            'Dexter'
        """
        logger.debug("Getting show with id {0} with language {1}".format(series_id, language))

        if language != 'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError("{0} is not a valid language".format(language))

        context = {'seriesid': series_id, "language": language,
                   'mirror': self.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key']}

        url = __series__.format(**context)
        try:
            data = self.loader.load(url, cache)
        except error.TVDBNotFoundError:
            logger.debug("Id {0} not found".format(series_id))
            raise error.TVDBIdError("Series id {0} not found".format(series_id))
        except error.ConnectionError as _error:
            logger.debug("Unable to connect to URL: {0}. {1}".format(url, _error))
            raise

        if data.strip():
            data = generate_tree(data)
        else:
            logger.debug("Empty data received for id {0}".format(series_id))
            raise error.TVDBIdError("No Show with id {0} found".format(series_id))

        series = parse_xml(data, "Series")
        assert len(series) <= 1, "Should not find more than one series"

        if len(series) >= 1:
            return Show(series[0], self, language, self.config)
        else:
            raise error.TVDBIdError("No Show with id {0} found".format(series_id))

    # pylint: disable=W0105
    get_series = get
    """
    .. versionadded:: 0.4

    An alias for the :func:`get` function to make it clearer what is being fetched.
    """
    # pylint: enable=W0105

    def get_episode(self, episode_id, language, cache=True):
        """
        .. versionadded:: 0.4

        :param episode_id: The Episode Id to fetch
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
                    resources will be reloaded from server.

        :return: An :class:`Episode()` instance
        :raise: :class:`pytvdbapi.error.TVDBIdError` if no episode is found with the given Id


        Given a valid episode Id the corresponding episode data is fetched and
        the :class:`Episode()` instance is returned.

        .. Note:: When the :class:`Episode()` is loaded using :func:`get_episode()`
            the episode attribute will be None.

        Example::

            >>> from pytvdbapi import api
            >>> db = api.TVDB("B43FF87DE395DF56")
            >>> episode = db.get_episode(308834, "en")
            >>> episode.id
            308834
            >>> episode.EpisodeName
            'Crocodile'

        """

        logger.debug("Getting episode with id {0} with language {1}".format(episode_id, language))

        if language != 'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError("{0} is not a valid language".format(language))

        context = {'episodeid': episode_id, "language": language,
                   'mirror': self.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key']}

        url = __episode__.format(**context)

        try:
            data = self.loader.load(url, cache)
        except error.TVDBNotFoundError:
            raise error.TVDBIdError("No Episode with id {0} found".format(episode_id))
        except error.ConnectionError as _error:
            logger.debug("Unable to connect to URL: {0}. {1}".format(url, _error))
            raise

        if data.strip():
            data = generate_tree(data)
        else:
            logger.debug("Empty data received for id {0}".format(episode_id))
            raise error.TVDBIdError("No Episode with id {0} found".format(episode_id))

        episodes = parse_xml(data, "Episode")
        assert len(episodes) <= 1, "Should not find more than one episodes"

        if len(episodes) >= 1:
            return Episode(episodes[0], None, self.config)
        else:
            raise error.TVDBIdError("No Episode with id {0} found".format(episode_id))
