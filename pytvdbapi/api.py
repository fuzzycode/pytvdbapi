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
This is the main module for **pytvdbapi** intended for client usage. It contains functions to access the
API functionality through the :class:`TVDB` class and its methods. It has implementations for
representations of :class:`Show`, :class:`Season` and :class:`Episode` objects.

It also contains functionality to access the list of API supported languages through the :func:`languages`
function.

Basic usage::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56")
    >>> result = db.search("How I met your mother", "en")
    >>> len(result)
    1

    >>> show = result[0]  # If there is a perfect match, it will be the first
    >>> print(show.SeriesName)
    How I Met Your Mother

    >>> len(show)  # Show the number of seasons
    10

    >>> for season in show: #doctest: +ELLIPSIS
    ...     for episode in season:
    ...         print(episode.EpisodeName)
    ...
    Robin Sparkles Music Video - Let's Go to the Mall
    Robin Sparkles Music Video - Sandcastles In the Sand
    ...
    Pilot
    Purple Giraffe
    Sweet Taste of Liberty
    Return of the Shirt
    ...
"""
from __future__ import absolute_import, print_function
from collections import Sequence

import logging
import tempfile
import os
import datetime

# pylint: disable=E0611, F0401
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


from pytvdbapi.actor import Actor
from pytvdbapi.banner import Banner
from pytvdbapi.urls import (mirrors, search, zap2itid, imdbid, series, episode, airdate, absolute_order,
                            dvd_order, default_order, actors, banners)
from pytvdbapi.utils import unicode_arguments, deprecate_episode_id, InsensitiveDictionary
from pytvdbapi._compat import implements_to_string, make_bytes, make_unicode, text_type, int_types
from pytvdbapi import error
from pytvdbapi.__init__ import __NAME__
from pytvdbapi.loader import Loader
from pytvdbapi.mirror import MirrorList, TypeMask
from pytvdbapi.xmlhelpers import parse_xml, generate_tree, has_element


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

        self.data.update(InsensitiveDictionary(show_data[0], ignore_case=self.ignore_case))

        for episode_data in episodes:
            season_nr = int(episode_data['SeasonNumber'])
            if season_nr not in self.seasons:
                self.seasons[season_nr] = Season(season_nr, self)

            episode_instance = Episode(episode_data, self.seasons[season_nr], self.config)
            self.seasons[season_nr].append(episode_instance)

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

        :param key: A callable taking an :class:`Episode` instance as argument and returns a boolean
        :returns: An :class:`Episode` instance or None

        Finds the first :class:`Episode` for witch :code:`key` returns :code:`True`.

        .. note::
            The order in which the :class:`Episode` instances are searched is not guaranteed and the first
            match found is not necessarily the first one in a chronological sense.

        .. seealso:: :func:`Season.find` for information on finding an episode in a specific season
        """
        for season in self:
            _episode = season.find(key=key)
            if _episode is not None:
                return _episode
        return None

    def filter(self, key):
        """
        .. versionadded:: 0.5

        :param key: A callable taking an :class:`Episode` instance as argument and returns a boolean
        :returns: A list of 0 or more :class:`Episode` instances

        Finds all :class:`Episode` instances for witch :code:`key` returns :code:`True`.

        .. seealso:: :func:`Season.filter` for information on filtering episodes in a specific season
        """
        result = list()
        for season in self:
            result.extend(season.filter(key=key))
        return result


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


__all__ = ['languages', 'Language', 'TVDB', 'Search', 'Show', 'Season', 'Episode']

# Module logger object
logger = logging.getLogger(__name__)


@implements_to_string
class Language(object):
    """
    Representing a language that is supported by the API.

    .. seealso:: :func:`TVDB.get_series`, :func:`TVDB.get_episode` and :func:`TVDB.search` for functions
        where the language can be specified.
    """

    def __init__(self, abbrev, name, language_id):
        # : A two letter abbreviation representing the language, e.g. *en*.
        #: This is what should be passed when specifying a language to the API.
        self.abbreviation = abbrev

        #: The localised name of the language.
        self.name = name

        self._id = language_id

    def __str__(self):
        return u'<{0} - {1}({2})>'.format(self.__class__.__name__, self.name, self.abbreviation)

    def __repr__(self):
        return self.__str__()


# The list of API supported languages
__LANGUAGES__ = {u"da": Language(abbrev=u"da", name=u"Dansk", language_id=10),
                 u"fi": Language(abbrev=u"fi", name=u"Suomeksi", language_id=11),
                 u"nl": Language(abbrev=u"nl", name=u"Nederlands", language_id=13),
                 u"de": Language(abbrev=u"de", name=u"Deutsch", language_id=14),
                 u"it": Language(abbrev=u"it", name=u"Italiano", language_id=15),
                 u"es": Language(abbrev=u"es", name=u"Español", language_id=16),
                 u"fr": Language(abbrev=u"fr", name=u"Français", language_id=17),
                 u"pl": Language(abbrev=u"pl", name=u"Polski", language_id=18),
                 u"hu": Language(abbrev=u"hu", name=u"Magyar", language_id=19),
                 u"el": Language(abbrev=u"el", name=u"Ελληνικά", language_id=20),
                 u"tr": Language(abbrev=u"tr", name=u"Türkçe", language_id=21),
                 u"ru": Language(abbrev=u"ru", name=u"русский язык", language_id=22),
                 u"he": Language(abbrev=u"he", name=u" עברית", language_id=24),
                 u"ja": Language(abbrev=u"ja", name=u"日本語", language_id=25),
                 u"pt": Language(abbrev=u"pt", name=u"Português", language_id=26),
                 u"zh": Language(abbrev=u"zh", name=u"中文", language_id=27),
                 u"cs": Language(abbrev=u"cs", name=u"čeština", language_id=28),
                 u"sl": Language(abbrev=u"sl", name=u"Slovenski", language_id=30),
                 u"hr": Language(abbrev=u"hr", name=u"Hrvatski", language_id=31),
                 u"ko": Language(abbrev=u"ko", name=u"한국어", language_id=32),
                 u"en": Language(abbrev=u"en", name=u"English", language_id=7),
                 u"sv": Language(abbrev=u"sv", name=u"Svenska", language_id=8),
                 u"no": Language(abbrev=u"no", name=u"Norsk", language_id=9)}


def languages():
    """
    :return: A list of :class:`Language` objects

    Returns the list of all API supported languages.

    Example::

        >>> from pytvdbapi import api
        >>> for language in api.languages():  #doctest: +ELLIPSIS
        ...     print(language)
        <Language - čeština(cs)>
        <Language - Dansk(da)>
        <Language - Deutsch(de)>
        ...
        <Language - English(en)>
        ...
        <Language - Svenska(sv)>
        ...
    """
    return sorted([lang for lang in __LANGUAGES__.values()], key=lambda l: l.abbreviation)


class Search(object):
    """
    :raise: :exc:`pytvdbapi.error.TVDBIndexError`

    A search result returned from calling :func:`TVDB.search()`. It supports
    iterating over the results, and the individual shows matching the search
    can be accessed using the [ ] syntax.

    The search will contain 0 or more :class:`Show()` instances matching the
    search.

    The shows will be stored in the same order as they are returned from
    `thetvdb.com <http://thetvdb.com>`_. They state that if there is a
    perfect match to the search, it will be the first element returned.

    .. seealso:: :func:`TVDB.search` for an example of how to use the search
    """

    def __init__(self, result, search_phrase, language):
        self._result = result

        # The search term used to generate the search result
        self.search = search_phrase

        # The language used to perform the search
        self.language = language

    def __len__(self):
        return len(self._result)

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise error.TVDBValueError(u"Index should be an integer")

        try:
            return self._result[item]
        except (IndexError, TypeError):
            raise error.TVDBIndexError(u"Index out of range ({0})".format(item))

    def __iter__(self):
        return iter(self._result)


class TVDB(object):
    """
    :param api_key: The API key to use to communicate with the server
    :param kwargs:

    This is the main entry point for the API. The functionality of the API is
    controlled by configuring the keyword arguments. The supported keyword
    arguments are:

    * **cache_dir** (default=/<system tmp dir>/pytvdbapi/). Specifies the
      directory to use for caching the server requests.

    .. versionadded:: 0.3

    * **actors** (default=False) The extended actor information is stored in a
      separate XML file and would require an additional request to the server
      to obtain. To limit the resource usage, the actor information will only
      be loaded when explicitly requested.

      .. note:: The :class:`Show()` object always contain a list of actor
        names.

    * **banners** (default=False) The extended banner information is stored in a
      separate XML file and would require an additional request to the server
      to obtain. To limit the resource usage, the banner information will only
      be loaded when explicitly requested.

    .. versionadded:: 0.4

    * **ignore_case** (default=False) If set to True, all attributes on the
      :class:`Show` and :class:`Episode` instances will be accessible in a
      case insensitive manner. If set to False, the default, all
      attributes will be case sensitive and retain the same casing
      as provided by `thetvdb.com <http://thetvdb.com>`_.

    * **timeout** (default=None) When set to a number, will cause the http
    request to timeout after that number of seconds.

    """

    @unicode_arguments
    def __init__(self, api_key, **kwargs):
        self.config = dict()

        # cache old searches to avoid hitting the server
        self.search_buffer = dict()

        # extract all argument and store for later use
        self.config['api_key'] = api_key
        self.config['cache_dir'] = kwargs.get("cache_dir",
                                              make_unicode(os.path.join(tempfile.gettempdir(), __NAME__)))

        self.config['actors'] = kwargs.get('actors', False)
        self.config['banners'] = kwargs.get('banners', False)
        self.config['ignore_case'] = kwargs.get('ignore_case', False)

        # Create the loader object to use
        self.loader = Loader(self.config['cache_dir'], timeout=kwargs.get('timeout', None))

        # Create the list of available mirrors
        tree = generate_tree(self.loader.load(mirrors.format(**self.config)))
        self.mirrors = MirrorList(tree)

    @unicode_arguments
    def search(self, show, language, cache=True):
        """
        :param show: The show name to search for
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
            resources will be reloaded from server.
        :return: A :class:`Search()` instance
        :raise: :exc:`pytvdbapi.error.TVDBValueError`

        Searches the server for a show with the provided show name in the
        provided language. The language should be one of the supported
        language abbreviations or it could be set to *all* to search all
        languages. It will raise :class:`pytvdbapi.error.TVDBValueError` if
        an invalid language is provided.

        Searches are always cached within a session to make subsequent
        searches with the same parameters fast. If *cache*
        is set to True searches will also be cached across sessions,
        this is recommended to increase speed and to reduce the workload of
        the servers.

        Example::

            >>> from pytvdbapi import api
            >>> db = api.TVDB("B43FF87DE395DF56")
            >>> result = db.search("House", "en")

            >>> print(result[0])
            <Show - House>

            >>> for show in result:
            ...     print(show) # doctest: +ELLIPSIS
            <Show - House>
            ...
        """

        logger.debug(u"Searching for {0} using language {1}".format(show, language))

        if language != u'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError(u"{0} is not a valid language".format(language))

        if (show, language) not in self.search_buffer or not cache:
            context = {'series': quote(make_bytes(show)), "language": language}
            data = generate_tree(self.loader.load(search.format(**context), cache))
            shows = [Show(d, self, language, self.config) for d in parse_xml(data, "Series")]

            self.search_buffer[(show, language)] = shows

        return Search(self.search_buffer[(show, language)], show, language)

    @unicode_arguments
    def get_series(self, series_id, language, id_type='tvdb', cache=True):
        """
        .. versionadded:: 0.4
        .. versionchanged:: 0.5 Added *id_type* parameter

        :param series_id: The Show Id to fetch
        :param language: The language abbreviation to search for. E.g. "en"
        :param id_type: Information about what kind of id is provided. Should be one of *('tvdb', 'imdb',
            'zap2it')*
        :param cache: If False, the local cache will not be used and the
                    resources will be reloaded from server.

        :return: A :class:`Show()` instance
        :raise: :exc:`pytvdbapi.error.TVDBValueError`, :exc:`pytvdbapi.error.TVDBIdError`

        Provided a valid Show ID, the data for the show is fetched and a
        corresponding :class:`Show()` object is returned.

        Example::

            >>> from pytvdbapi import api
            >>> db = api.TVDB("B43FF87DE395DF56")
            >>> show = db.get_series( 79349, "en" )  # Load Dexter
            >>> print(show.SeriesName)
            Dexter
        """
        if id_type not in ('tvdb', 'imdb', 'zap2it'):
            raise error.TVDBValueError("Invalid id type")
        elif language != 'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError(u"{0} is not a valid language".format(language))

        # Map id type to url template
        __url__ = {'tvdb': series, 'imdb': imdbid, 'zap2it': zap2itid}

        try:
            series_id = text_type(series_id)
        except ValueError:
            raise error.TVDBValueError(
                "Invalid id type, expected {0} or {1}, got {2}".format(text_type, int_types, type(series_id)))

        if id_type == 'imdb':
            series_id = series_id[2:] if series_id.startswith('tt') else series_id
        elif id_type == 'zap2it':
            series_id = series_id if series_id.startswith('EP') else u'EP' + series_id.rjust(8, '0')

        logger.debug(
            u"Getting series with id {0}({2}) with language {1}".format(series_id, language, id_type))

        context = {'seriesid': series_id, "language": language,
                   'mirror': self.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key'], 'imdbid': series_id, 'zap2itid': series_id}

        url = __url__[id_type].format(**context)
        logger.debug(u'Getting series from {0}'.format(url))

        try:
            data = self.loader.load(url, cache)
        except error.TVDBNotFoundError:
            raise error.TVDBIdError(u"Series id {0} not found".format(series_id))

        data = generate_tree(data)

        series_data = parse_xml(data, "Series")

        if len(series) == 0:
            raise error.BadData("Bad data received")
        else:
            return Show(series_data[0], self, language, self.config, data)

    @unicode_arguments
    @deprecate_episode_id
    def get_episode(self, language, method="id", cache=True, **kwargs):
        """
        .. versionadded:: 0.4
        .. versionchanged:: 0.5 Added the possibility to get an episode using *default*, *dvd*, and *absolute*
            sort order

        :param episode_id: *Deprecated in 0.5* Use the *episodeid* keyword argument with the *id*
            method instead
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
                    resources will be reloaded from server.
        :param method: (default=id) Specify what method should be used to get the episode. Depending on
            what method is specified, different parameters must be passed as keyword arguments. Should be one
            of (id, default, dvd, absolute).
        :param kwargs: *episodeid*, *seriesid*, *seasonnumber*, *episodenumber* and *absolutenumber*. See
            the examples for information on how to use them.
        :return: An :class:`Episode()` instance
        :raise: :exc:`pytvdbapi.error.TVDBValueError`, :exc:`pytvdbapi.error.BadData`

        Retrieves a single episode. Depending on what method is specified different criteria can be used to
        retrieve the episode.

        Examples:

        Load an episode using the episode id

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> ep = db.get_episode("en", episodeid=308834)  # id is the default method
        >>> print(ep.EpisodeName)
        Crocodile

        Load an episode using dvd and default sort order

        >>> ep = db.get_episode("en", "dvd", seasonnumber=2, episodenumber=5, seriesid=79349)
        >>> print(ep.EpisodeName)
        The Dark Defender

        >>> ep = db.get_episode("en", "default", seasonnumber=2, episodenumber=6, seriesid=79349)
        >>> print(ep.EpisodeName)
        Dex, Lies, and Videotape

        Load an episode using the absolute number

        >>> ep = db.get_episode("en", "absolute", absolutenumber=19, seriesid=79349)
        >>> print(ep.EpisodeName)
        That Night, A Forest Grew

        Under some circumstances the backend server fails to return a proper **404** file not found error
        response when the requested episode can not be found, but instead returns a valid HTML file with
        the content *404 file not found*. For this reason it is required to check for both
        :exc:`pytvdbapi.error.TVDBValueError` and :exc:`pytvdbapi.error.BadData` to detect an issue
        downloading the episode.

        >>> from pytvdbapi.error import BadData
        >>> from pytvdbapi.error import TVDBNotFoundError
        >>> try:
        ...    ep = db.get_episode("en", episodeid=308834)
        ... except TVDBNotFoundError:
        ...    # this is the standard 404 error code returned from the server
        ...    pass
        ... except BadData:
        ...     # This is when the server returns a 200 code but with a HTML page saying 404 Nothing found
        ...     pass

        .. Note:: When the :class:`Episode()` is loaded using :func:`get_episode()`
            the *season* attribute used to link the episode with a season will be None.
        """
        methods = {"default": default_order, "dvd": dvd_order, "absolute": absolute_order, "id": episode}

        if language != 'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError(u"{0} is not a valid language".format(language))

        context = {"language": language,
                   'mirror': self.mirrors.get_mirror(TypeMask.XML).url,
                   'api_key': self.config['api_key']}

        kwargs.update(context)

        try:
            url = methods[method]
        except KeyError:
            raise error.TVDBValueError(u"{0} is not a valid get method".format(method))

        try:
            url = url.format(**kwargs)
        except KeyError:
            raise error.TVDBValueError("Missing arguments for method {0}".format(method))

        logger.debug(u'Getting episode from {0}'.format(url))

        data = self.loader.load(url, cache)
        data = generate_tree(data)

        episodes = parse_xml(data, "Episode")

        if len(episodes) == 0:
            raise error.BadData("Bad data received")
        else:
            return Episode(episodes[0], None, self.config)

    @unicode_arguments
    def get_episode_by_air_date(self, series_id, language, air_date, cache=True):
        """
        .. versionadded:: 0.5

        :param series_id: The TVDB series id of the episode
        :param language: The language to search for. Should be a two letter abbreviation e.g. *en*.
        :param air_date: The air date to search for. Should be of type :class:`datetime.date`
        :type air_date: datetime.date
        :param cache: If False, the local cache will not be used and the
                    resources will be reloaded from server.

        :return: If found, an :class:`Episode` instance
        :raise: :exc:`pytvdbapi.error.TVDBValueError`


        .. Note:: When the :class:`Episode()` is loaded using :func:`get_episode_by_air_date`
            the *season* attribute used to link the episode with a season will be None.
        """
        if type(air_date) not in (datetime.date,):
            raise error.TVDBValueError("air_date should be of type datetime.date")
        elif language != 'all' and language not in __LANGUAGES__:
            raise error.TVDBValueError(u"{0} is not a valid language".format(language))

        context = {'seriesid': series_id, 'airdate': air_date, "language": language,
                   'mirror': self.mirrors.get_mirror(TypeMask.XML).url, 'api_key': self.config['api_key']}

        url = airdate.format(**context)
        logger.debug(u'Getting episode from {0}'.format(url))

        data = self.loader.load(url, cache)

        data = generate_tree(data)

        # The xml has an "Error" element in it if no episode was found
        if has_element(data, 'Error'):
            raise error.TVDBNotFoundError(u"".format())

        episodes = parse_xml(data, "Episode")

        if len(episodes) == 0:
            raise error.BadData("Bad data received")
        else:
            return Episode(episodes[0], None, self.config)


@implements_to_string
class Season(Sequence):
    """
    :raise: :exc:`pytvdbapi.error.TVDBIndexError`

    Holds all the episodes that belong to a specific season. It is possible
    to iterate over the Season to obtain the individual :class:`Episode`
    instances. It is also possible to obtain an individual episode using the
    [ ] syntax. It will raise :class:`pytvdbapi.error.TVDBIndexError` if trying
    to index an invalid episode index.

    It is possible to obtain the containing :class:`Show` instance through the
    *Season.show* attribute.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> result = db.search("Dexter", "en")
        >>> show = result[0]

        >>> season = show[2]
        >>> len(season)  # Number of episodes in the season
        12

        >>> print(season.season_number)
        2

        >>> print(season[2].EpisodeName)
        Waiting to Exhale

        >>> for ep in season: #doctest: +ELLIPSIS
        ...     print(ep.EpisodeName)
        ...
        It's Alive!
        Waiting to Exhale
        An Inconvenient Lie
        See-Through
        ...
        Left Turn Ahead
        The British Invasion
    """

    def __init__(self, season_number, show):
        self.show, self.season_number = show, season_number
        self.episodes = dict()

    def __getitem__(self, item):
        if isinstance(item, int):
            try:
                return self.episodes[item]
            except KeyError:
                raise error.TVDBIndexError(u"Episode {0} not found".format(item))

        elif isinstance(item, slice):
            indices = sorted(self.episodes.keys())[item]  # Slice the keys
            return [self[i] for i in indices]
        else:
            raise error.TVDBValueError(u"Index should be an integer")

    def __dir__(self):  # pylint: disable=R0201
        return ['show', 'season_number']

    def __reversed__(self):
        for i in sorted(self.episodes.keys(), reverse=True):
            yield self[i]

    def __len__(self):
        return len(self.episodes)

    def __iter__(self):
        return iter(sorted(list(self.episodes.values()), key=lambda ep: ep.EpisodeNumber))

    def __str__(self):
        return u'<Season {0:03}>'.format(self.season_number)

    def __repr__(self):
        return self.__str__()

    def append(self, episode_instance):
        """
        :param episode_instance: The episode_instance to append
        :type episode_instance: :class:`Episode`

        Adds a new :class:`Episode` to the season. If an episode_instance with the same
        EpisodeNumber already exists, it will be overwritten.
        """
        assert type(episode_instance) in (Episode,)
        logger.debug(u"{0} adding episode_instance {1}".format(self, episode_instance))

        self.episodes[int(episode_instance.EpisodeNumber)] = episode_instance

    def find(self, key):
        """
        .. versionadded:: 0.5

        :param key: A callable taking an :class:`Episode` instance as argument and returns a boolean
        :raises: :class:`pytvdbapi.error.TypeError`
        :returns: An :class:`Episode` instance or None if no match was found

        Return the first :class:`Episode` for witch :code:`key` returns :code:`True`
        """
        try:
            return next(ep for ep in self.episodes.values() if key(ep))
        except StopIteration:  # Nothing found
            return None
        except TypeError as _error:
            raise error.TVDBTypeError("{0}".format(_error))

    def filter(self, key):
        """
        .. versionadded:: 0.5

        :param key: A callable taking an :class:`Episode` instance as argument and returns a boolean
        :raises: :class:`pytvdbapi.error.TypeError`
        :returns: list with 0 or more :class:`Episode` instances

        Return a list of all :class:`Episode` instances for witch :code:`key` returns :code:`True`
        """
        try:
            return [ep for ep in self.episodes.values() if key(ep)]
        except TypeError as _error:
            raise error.TVDBTypeError("{0}".format(_error))
