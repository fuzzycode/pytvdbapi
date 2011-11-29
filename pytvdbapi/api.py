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
A small, clean and easy to use API for the pytvdbapi.com online DB service. It
is designed to be fast, easy to use and to respect the functionality of the
pytvdbapi.com API.

This module is the public interface for the package.

Usage::

    >>> from pytvdbapi import api
    >>> db = api.tvdb("B43FF87DE395DF56")
    >>> search = db.search("How I met your mother", "en")
    >>> show = search[0]
    >>> show.SeriesName
    'How I Met Your Mother'
"""

import tempfile
import urllib
import os
import sys
from pytvdbapi import error, get_logger
from pytvdbapi.__init__ import __NAME__ as name
from pytvdbapi.language import LanguageList
from pytvdbapi.loader import Loader
from pytvdbapi.mirror import MirrorList, TypeMask
from pytvdbapi.utils import merge
from pytvdbapi.xmlhelpers import parse_xml, generate_tree

__all__ = ['Episode', 'Season', 'Show', 'Search', 'tvdb']

#Module logger object
logger = get_logger(__name__)

# List the URLs that we need
urls = dict(mirrors="http://www.thetvdb.com/api/%(api_key)s/mirrors.xml",
    time="http://www.thetvdb.com/api/Updates.php?type=none",
    languages="http://www.thetvdb.com/api/%(api_key)s/languages.xml",
    search=("http://www.thetvdb.com/api/GetSeries.php?seriesname=%(series)s&language=%(language)s"),
    series=("%(mirror)s/api/%(api_key)s/series/%(seriesid)s/all/%(language)s.xml"))


class Episode(object):
    """
    :raise: TVDBAttributeError

    Holds all information about an individual episode. This should be treated
    as a read-only object to obtain the attributes of the episode.

    All episode values returned from pytvdbapi.com_ are
    accessible as attributes of the episode object. The attributes will be
    named exactly as returned from pytvdbapi.com_ and are case sensitive.
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
        >>> db = api.tvdb("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> show = search[0]
        >>> episode = show[1][5]
        >>> dir(episode)
        ['Combined_episodenumber', 'Combined_season', 'DVD_chapter', 'DVD_discid', 'DVD_episodenumber', 'DVD_season', 'Director', 'EpImgFlag', 'EpisodeName', 'EpisodeNumber', 'FirstAired', 'GuestStars', 'IMDB_ID', 'Language', 'Overview', 'ProductionCode', 'Rating', 'RatingCount', 'SeasonNumber', 'Writer', 'absolute_number', 'filename', 'id', 'lastupdated', 'season', 'seasonid', 'seriesid']
        >>> episode.EpisodeName
        'Love American Style'
        >>> episode.GuestStars
        ['Terry Woodberry', ' Carmen Olivares', ' Ashley Rose Orr', ' Demetrius Grosse', ' Monique Curnen', ' June Angela', ' Valerie Dillman', ' Brad Henke', ' Jose Zuniga', ' Allysa Tacher', ' Lizette Carrion', ' Norma Fontana', ' Minerva Garcia', ' Josh Daugherty', ' Geoffrey Rivas']
        >>> episode.FirstAired
        datetime.date(2006, 10, 29)
        >>> episode.season
        <Season 001>

    .. _pytvdbapi.com: http://pytvdbapi.com
    """
    def __init__(self, data, season):
        self.data, self.season = data, season

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            logger.error(u"Episode has no attribute {0}".format(item))
            raise error.TVDBAttributeError(u"Episode has no attribute {0}"
            .format(item))

    def __dir__(self):
        return self.data.keys() + \
               [d for d in self.__dict__.keys() if d != "data"]
    
    def __repr__(self):
        try:
            return u"<Episode S{0:03d}E{1:03d} - {2}>".format(
                                                int(self.SeasonNumber),
                                                int(self.EpisodeNumber),
                                                self.EpisodeName)
        except error.TVDBAttributeError:
            return u"<Episode>"

class Season(object):
    """
    :raise: TVDBIndexError

    Holds all the episodes that belong to a specific season. It is possible
    to iterate over the Season to obtain the individual :class:`Episode`
    instances. It is also possible to obtain an individual episode using the
    [ ] syntax. It will raise :class:`error.TVDBIndexError` if trying to index
    an invalid episode index.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.tvdb("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> show = search[0]
        >>> seson = show[1]
        >>> season = show[1]
        >>> len(season)
        12
        >>> season[3]
        <Episode S001E003 - Popping Cherry>
        >>> for episode in season:
        ...     print episode
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
            logger.error(u"Episode {0} not found".format(item))
            raise error.TVDBIndexError("Index {0} not found".format(item))

    def __len__(self):
        return len(self.episodes)
    
    def __iter__(self):
        return iter(sorted(self.episodes.values(),
            cmp=lambda lhs, rhs: cmp(int(lhs.EpisodeNumber),
                                     int(rhs.EpisodeNumber))))

    def __repr__(self):
        return u"<Season {0:03}>".format( self.season_number )

    def append(self, episode):
        assert type(episode) in (Episode,)
        logger.debug(u"{0} adding episode {1}".
                    format(self, episode))

        self.episodes[int(episode.EpisodeNumber)] = episode


class Show(object):
    """
    :raise: TVDBAttributeError, TVDBIndexError

    Holds attributes about a single show and contains all seasons associated
    with a show. The attributes are named exactly as returned from pytvdbapi.com_.
    This object should be considered a read only container of data
    provided from the server. Some type conversion of of the attributes will
    take place as follows:

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

    .. note:: When searching, pytvdbapi.com_ provides a basic set of attributes
        for the show. When the full data set is loaded pytvdbapi.com_ provides a
        complete set of attributes for the show. The full data set is loaded when
        accessing the season data of the show. If you need access to the full set
        of attributes you can force the loading of the full data set by calling
        the :func:`update()` function.


    Example::

        >>> from pytvdbapi import api
        >>> db = api.tvdb("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> show = search[0]
        >>> dir(show)
        ['FirstAired', 'IMDB_ID', 'Overview', 'SeriesName', 'api', 'banner', 'id', 'lang', 'language', 'seasons', 'seriesid', 'zap2it_id']
        >>> show.update()
        >>> dir(show)
        ['Actors', 'Airs_DayOfWeek', 'Airs_Time', 'ContentRating', 'FirstAired', 'Genre', 'IMDB_ID', 'Language', 'Network', 'NetworkID', 'Overview', 'Rating', 'RatingCount', 'Runtime', 'SeriesID', 'SeriesName', 'Status', 'added', 'addedBy', 'api', 'banner', 'fanart', 'id', 'lang', 'language', 'lastupdated', 'poster', 'seasons', 'seriesid', 'zap2it_id']
        >>> len(show)
        7
        >>> show[5]
        <Season 005>
        >>> for season in show:
        ...     print season
        ...
        <Season 000>
        <Season 001>
        <Season 002>
        <Season 003>
        <Season 004>
        <Season 005>
        <Season 006>


    .. _pytvdbapi.com: http://pytvdbapi.com
    """
    def __init__(self, data, api, language):
        self.api, self.data, self.lang = api, data, language
        self.seasons = dict()

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            logger.debug( u"Attribute not found" )
            raise error.TVDBAttributeError(u"Show has no attribute names %s" %
                                           item)

    def __repr__(self):
        return "<Show - {0}>".format(self.SeriesName)

    def __dir__(self):
        return self.data.keys() + \
               [d for d in self.__dict__.keys() if d != "data"]

    def __iter__(self):
        if not self.seasons:
            self._populate_data()

        return iter(sorted(self.seasons.values(),
            cmp=lambda lhs, rhs: cmp(int(lhs.season_number),
                                     int(rhs.season_number))))

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
            logger.error(u"Season {0} not found".format(item))
            raise error.TVDBIndexError()

    def update(self):
        """
        Updates the data structure with data from the server.
        """
        self._populate_data()

    def _populate_data(self):
        logger.debug(u"Populating season data from URL.")
        
        context = {'mirror':self.api.mirrors.get_mirror(TypeMask.XML).url,
                       'api_key':self.api.config['api_key'],
                       'seriesid':self.id,
                       'language':self.lang}

        data = generate_tree(self.api.loader.load(urls['series'] % context))
        episodes = [d for d in parse_xml( data, "Episode")]

        show_data = parse_xml(data, "Series")
        assert len(show_data) == 1, u"there should only be 1 Series element in\
        the xml data"

        self.data = merge( self.data, show_data[0] )

        for episode in episodes:
            season_nr = int(episode['SeasonNumber'])
            if not season_nr in self.seasons:
                self.seasons[ season_nr ] = Season(season_nr, self)

            ep = Episode( episode, self.seasons[season_nr] )
            self.seasons[season_nr].append(ep)

    
class Search(object):
    """
    A search result returned from calling :func:`tvdb.search()`. It supports
    iterating and the individual shows matching the search can be accessed
    using the [ ] syntax.

    The search will contain 0 or more :class:`Show()` instances matching the
    search.

    The shows will be stored in the same order as they are returned from
    `pytvdbapi.com <http://pytvdbapi.com>`_. They state that if there is a
    perfect match to the search, it will be the first element returned.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.tvdb("B43FF87DE395DF56")
        >>> search = db.search("Dexter", "en")
        >>> for s in search:
        ...     print s
        ...
        <Show - Dexter>
        <Show - Cliff Dexter>
    """
    
    def __init__(self, result, search, language):
        self.result, self.search, self.language = result, search, language

    def __len__(self):
        return len(self.result)

    def __getitem__(self, item):
        try:
            return self.result[item]
        except (IndexError, TypeError):
            logger.warning("Index out of range")
            raise error.TVDBIndexError("Index out of range")

    def __iter__(self):
        return iter(self.result)


class tvdb(object):
    """
    :param api_key: The API key to use to communicate with the server
    :param kwargs:

    This is the main entry point for the API. The functionality of the API is
    controlled by configuring the key word arguments. The supported key word
    arguments are:

    * *force_lang* default=False. If set to True, the API will reload the\
        language list from the server. If False, the local preloaded file\
        will be used. The language list is relative stable but if there are\
        changes it could be useful to set this to True to obtain a new version\
        from the server. It is only necessary to do this once since the API\
        stores the reloaded data for further use.
    * *cache_dir* default=/tmp/pytvdbapi/. Specifies the directory to use\
        for caching the server requests. It will default to a directory\
        within the platform specific temp folder.\

        
    """

    def __init__(self, api_key, **kwargs):
        self.config = dict()

        #cache old searches to avoid hitting the server
        self.search_buffer = dict()

        #Store the path to where we are
        self.path = os.path.abspath(os.path.dirname(__file__))

        #extract all argument and store for later use
        self.config['force_lang'] = getattr(kwargs, 'force_lang', False)
        self.config['api_key'] = api_key
        self.config['cache_dir'] = getattr(kwargs, 'cache_dir',
                os.path.join(tempfile.gettempdir(), name))

        #Create the loader object to use
        self.loader = Loader(self.config['cache_dir'])

        #If requested, update the local language file from the server
        if self.config['force_lang']:
            logger.debug("updating Language file from server")
            with open(os.path.join(self.path, '../data/languages.xml'),
                                   'wt') as f:
                f.write(self.loader.load(urls['languages'] % self.config))

        #Setup the list of supported languages
        self.languages = LanguageList(
            generate_tree(open(os.path.join(self.path,
                                    '../data/languages.xml'), 'rt').read()))

        #Create the list of available mirrors
        self.mirrors = MirrorList(
            generate_tree(self.loader.load(urls['mirrors'] % self.config)))

    def search(self, show, language, cache=True):
        """
        :param show: The show name to search for
        :param language: The language abbreviation to search for. E.g. "en"
        :param cache: If False, the local cache will not be used and the
            resources will be reloaded from server.
        :return: A :class:`Search()` instance
        :raise: TVDBValueError

        Searches the server for a show with the provided show name in the
        provided language. The language should be one of the supported
        language abbreviations or it could be set to *all* to search all
        languages. It will raise :class:`TVDBValueError` if an invalid
        language is provided.

        Searches are always cached within a session to make subsequent
        searches with the same parameters really cheap and fast. If *cache*
        is set to True searches will also be cached across sessions,
        this is recommended to increase speed and to reduce the workload of
        the servers.

        Example::
        
            >>> from pytvdbapi import api
            >>> db = api.tvdb("B43FF87DE395DF56")
            >>> search = db.search("Dexter", "en")
            >>> for s in search:
            ...     print s
            ...
            <Show - Dexter>
            <Show - Cliff Dexter>

        """
        
        logger.debug("Searching for {0} using language {1}"
            .format(show, language))

        if language != 'all' and language not in self.languages:
            raise error.TVDBValueError("{0} is not a valid language")

        if (show, language) not in self.search_buffer:
            context = {'series': urllib.quote(show), "language":language}
            data = generate_tree(self.loader.load( urls['search'] % context,
                                                   cache ))
            shows = [Show(d, self, language)
                     for d in parse_xml(data, "Series")]

            self.search_buffer[(show, language)] = shows

        return Search(self.search_buffer[(show, language)], show, language)


#A small sample usage
if __name__ == '__main__':
    def main():
        import logging
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        logger.setLevel(logging.DEBUG)

        api = tvdb("B43FF87DE395DF56")
        search = api.search( "Dexter", "en" )

        for show in search:
            for season in show:
                for episode in season:
                    print episode

    sys.exit(main())