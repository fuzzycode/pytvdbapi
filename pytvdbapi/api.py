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

import logging
import tempfile
import os
import datetime

from pytvdbapi.episode import Episode
from pytvdbapi.show import Show
from pytvdbapi.urls import mirrors, search, zap2itid, imdbid, series, episode, airdate, absolute_order, \
    dvd_order, default_order
from pytvdbapi.utils import unicode_arguments, deprecate_episode_id
from pytvdbapi._compat import implements_to_string, make_bytes, make_unicode, text_type, int_types


try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from pytvdbapi import error
from pytvdbapi.__init__ import __NAME__
from pytvdbapi.loader import Loader
from pytvdbapi.mirror import MirrorList, TypeMask
from pytvdbapi.xmlhelpers import parse_xml, generate_tree, has_element

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

    def __init__(self, abbrev, name, id):
        # : A two letter abbreviation representing the language, e.g. *en*.
        #: This is what should be passed when specifying a language to the API.
        self.abbreviation = abbrev

        #: The localised name of the language.
        self.name = name

        self._id = id

    def __str__(self):
        return u'<{0} - {1}({2})>'.format(self.__class__.__name__, self.name, self.abbreviation)

    def __repr__(self):
        return self.__str__()


# The list of API supported languages
__LANGUAGES__ = {u"da": Language(abbrev=u"da", name=u"Dansk", id=10),
                 u"fi": Language(abbrev=u"fi", name=u"Suomeksi", id=11),
                 u"nl": Language(abbrev=u"nl", name=u"Nederlands", id=13),
                 u"de": Language(abbrev=u"de", name=u"Deutsch", id=14),
                 u"it": Language(abbrev=u"it", name=u"Italiano", id=15),
                 u"es": Language(abbrev=u"es", name=u"Español", id=16),
                 u"fr": Language(abbrev=u"fr", name=u"Français", id=17),
                 u"pl": Language(abbrev=u"pl", name=u"Polski", id=18),
                 u"hu": Language(abbrev=u"hu", name=u"Magyar", id=19),
                 u"el": Language(abbrev=u"el", name=u"Ελληνικά", id=20),
                 u"tr": Language(abbrev=u"tr", name=u"Türkçe", id=21),
                 u"ru": Language(abbrev=u"ru", name=u"русский язык", id=22),
                 u"he": Language(abbrev=u"he", name=u" עברית", id=24),
                 u"ja": Language(abbrev=u"ja", name=u"日本語", id=25),
                 u"pt": Language(abbrev=u"pt", name=u"Português", id=26),
                 u"zh": Language(abbrev=u"zh", name=u"中文", id=27),
                 u"cs": Language(abbrev=u"cs", name=u"čeština", id=28),
                 u"sl": Language(abbrev=u"sl", name=u"Slovenski", id=30),
                 u"hr": Language(abbrev=u"hr", name=u"Hrvatski", id=31),
                 u"ko": Language(abbrev=u"ko", name=u"한국어", id=32),
                 u"en": Language(abbrev=u"en", name=u"English", id=7),
                 u"sv": Language(abbrev=u"sv", name=u"Svenska", id=8),
                 u"no": Language(abbrev=u"no", name=u"Norsk", id=9)}


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

    def __init__(self, result, search, language):
        self._result = result

        # The search term used to generate the search result
        self.search = search

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
        self.loader = Loader(self.config['cache_dir'])

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
        .. versionchanged:: 0.5 Added the possibility to get an episode using default, dvd, and absolute
            sort order


        :param episode_id: *Deprecated in 0.5* Use the *episodeid* keyword argument with the *id*
            method instead
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
                    resources will be reloaded from server.
        :param method: (default=id) Specify what method should be used to get the episode. Depending on
            what method is specified, different parameters must be passed as keyword arguments. Should be one
            of (id, default, dvd, absolute).
        :param kwargs: Depending on the method used, you need to pass the following arguments:

            default:
                seriesid
                seasonnumber
                episodenumber

            dvd:
                seriesid
                seasonnumber
                episodenumber

            id:
                episodeid

            absolute:
                seriesid
                absolutenumber

        :return: An :class:`Episode()` instance
        :raise: :exc:`pytvdbapi.error.TVDBValueError`


        Example::

            >>> from pytvdbapi import api
            >>> db = api.TVDB("B43FF87DE395DF56")
            >>> episode = db.get_episode(308834, "en") # Load an episode of dexter
            >>> print(episode.id)
            308834

            >>> print(episode.EpisodeName)
            Crocodile

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
        except KeyError as e:
            raise error.TVDBValueError("")

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

        try:
            data = self.loader.load(url, cache)
        except error.TVDBNotFoundError:
            raise

        data = generate_tree(data)

        # The xml has an "Error" element in it if no episode was found
        if has_element(data, 'Error'):
            raise error.TVDBNotFoundError(u"".format())

        episodes = parse_xml(data, "Episode")

        if len(episodes) == 0:
            raise error.BadData("Bad data received")
        else:
            return Episode(episodes[0], None, self.config)
