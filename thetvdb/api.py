# -*- coding: utf-8 -*-

# This file is part of thetvdb.
#
# thetvdb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# thetvdb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with thetvdb.  If not, see <http://www.gnu.org/licenses/>.

"""
"""

import logging
import random
import tempfile
import httplib2
import os
import sys
from thetvdb import error
from thetvdb.__init__ import __NAME__ as name
import xml.etree.ElementTree as etree

#Module logger object
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# List the URLs that we need
urls = dict(mirrors="http://www.thetvdb.com/api/%(api_key)s/mirrors.xml",
    time="http://www.thetvdb.com/api/Updates.php?type=none",
    languages="http://www.thetvdb.com/api/%(api_key)s/languages.xml",
    search="http://www.thetvdb.com/api/GetSeries.php?seriesname=%(series)s",
    series=("%(mirror)s/api/%(api_key)s/series/%(seriesid)s/all/%(language)s.xml"))

def parser( xml_data, root = None ):
    """Converts the raw xml data into an element tree"""

    try:
        if type(xml_data) in (str, unicode):
            tree = etree.fromstring( xml_data )
        elif type(xml_data) in (bytes):
            tree = etree.parse(xml_data)
    except etree.ParseError:
        raise error.BadData("Invalid XML data passed")

    if root:
        return tree.find(root)
    else:
        return tree


def _parse_xml(etree, element):
    """

    :param etree:
    :param element:
    :return:
    """

    logger.debug("Parsing element tree for {0}".format(element))

    _list = list()
    for item in etree.findall( element ):
        _list.append( { i.tag:i.text for i in item.getchildren() } )

    logger.debug("Found {0} element".format(len(_list)))
    return _list

class TypeMask(object):
    """An enum like class with the mask flags for the mirrors"""
    XML = 1
    BANNER = 2
    ZIP = 4

class Mirror(object):
    """Stores data about a thetvdb.com mirror server"""

    def __init__(self, id, url, type_mask):
        self.id, self.url, self.type_mask = id, url, type_mask

    def __repr__(self):
        return "<{0} ({1}:{{2}})>".format(
            "Mirror", self.url, self.type_mask )


class MirrorList(object):
    """Managing a list available mirrors"""
    def __init__(self, etree):
        self.data = [
            Mirror(m['id'], m['mirrorpath'], m['typemask'])
            for m in _parse_xml( etree, 'Mirror' )
        ]

    def get_mirror(self, type_mask):
        try:
            return random.choice(
                [m for m in self.data if
                 int(m.type_mask) & int(type_mask) ==  int(type_mask)])
        except IndexError:
            raise error.TheTvDBError("No Mirror matching {0} found".
                format(type_mask))


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
            for lang in  _parse_xml( etree, "Language" ) ]

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        return self.data[item]

class Episode(object):
    def __init__(self, data, season):
        self.data, self.season = data, season

    def __getattr__(self, item):
        try:
            return self.data[item]
        except IndexError:
            logger.error("Episode has no attribute {0}".format(item))
            raise error.TVDBAttributeError

    def __repr__(self):
        try:
            return "<Episode {0}>".format(self.EpisodeName)
        except error.TVDBAttributeError:
            return "<Episode>"

class Season(object):
    def __init__(self, season_number, show):
        self.show, self.season_number = show, season_number
        self.episodes = dict()

    def __getitem__(self, item):
        try:
            return self.episodes[item]
        except IndexError:
            logger.error("Episode {0} not found".format(item))
            raise error.TVDBIndexError()

    def __iter__(self):
        return iter(sorted(self.episodes.items(),
            cmp=lambda lhs, rhs: cmp(lhs[1].EpisodeNumber,
                                     rhs[1].EpisodeNumber)))

    def __repr__(self):
        return "<Season {0}>".format( self.season_number )

    def append(self, episode):
        assert type(episode) in (Episode,)
        logger.debug("{0} adding episode {1}".
                    format(self, episode))

        self.episodes[int(episode.EpisodeNumber)] = episode


class Show(object):
    """Holds data about a show in thetvdb"""
    def __init__(self, data, api, language):
        self.api, self.data, self.language = api, data, language
        self.seasons = dict()

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            logger.debug( "Attribute not found" )
            raise error.TVDBAttributeError("Show has no attribute names %s" %
                                           item)

    def __iter__(self):
        if not self.seasons:
            self._populate_seasons()

        return iter(sorted(self.seasons.items(),
            cmp=lambda lhs, rhs: cmp(lhs[1].season_number,
                                     rhs[1].season_number)))


    def __getitem__(self, item):
        if not item in self.seasons:
            logger.debug("Season data missing, will load from url")
            self._populate_seasons()

        try:
            return self.seasons[item]
        except IndexError:
            logger.error("Season {0} not found".format(item))
            raise error.TVDBIndexError()


    def _populate_seasons(self):
        context = {'mirror':self.api.mirrors.get_mirror(TypeMask.ZIP).url,
                       'api_key':self.api.config['api_key'],
                       'seriesid':self.id,
                       'language':self.language}

        data = parser(self.api.loader.load(urls['series'] % context))
        episodes = [d for d in _parse_xml( data, "Episode")]

        for episode in episodes:
            season_nr = int(episode['SeasonNumber'])
            if not season_nr in self.seasons:
                self.seasons[ season_nr ] = Season(season_nr, self)

            ep = Episode( episode, self.seasons[season_nr] )
            self.seasons[season_nr].append(ep)

    
class Search(object):
    def __init__(self, result, search, language):
        self.result, self.search, self.language = result, search, language


class Loader(object):
    def __init__(self, cache_path):
        self.http = httplib2.Http( cache = os.path.abspath( cache_path ) )

    def load(self, url, cache=True):

        header = dict()
        if not cache:
            header['cache-control'] = 'no-cache'
            
        try:
            response, content = self.http.request( url, headers= header )
        except ( httplib2.RelativeURIError, httplib2.ServerNotFoundError ):
            raise error.ConnectionError(
                "Unable to connect to {0}".format(url))
        else:
            return content


class tvdb(object):
    """ """
    def __init__(self, **kwargs):
        self.config = dict()

        #cache old searches to avoid hitting the server
        self.search_buffer = dict()

        #extract all argument and store for later use
        self.config['force_lang'] = getattr(kwargs, 'force_lang', False)
        # TODO: Apply for a new api key for the new name??
        self.config['api_key'] = getattr(kwargs, 'api_key', 'B43FF87DE395DF56')
        self.config['cache_dir'] = getattr(kwargs, 'cache_dir',
                os.path.join(tempfile.gettempdir(), name))

        #Create the loader object to use
        self.loader = Loader(self.config['cache_dir'])
        #self.loader = BasicLoader()

        #If requested, update the local language file from the server
        if self.config['force_lang']:
            logger.debug("updating Language file from server")
            with open('../data/languages.xml', 'wt') as f:
                f.write(self.loader.load(urls['languages'] % self.config))

        #Setup the list of supported languages
        self.languages = LanguageList(
            parser(open('../data/languages.xml', 'rt').read()))

        #Create the list of available mirrors
        self.mirrors = MirrorList(
            parser(self.loader.load(urls['mirrors'] % self.config)))

    def search(self, show, language, cache=True):
        logger.debug("Searching for {0} using language {1}"
            .format(show, language))

        if (show, language) not in self.search_buffer:
            data = parser(self.loader.load( urls['search']
                            % {'series': show }, cache ))
            shows = [Show(d, self, language)
                     for d in _parse_xml(data, "Series")]

            self.search_buffer[(show, language)] = shows

        return Search(self.search_buffer[(show, language)], show, language)




#a small sample usage
if __name__ == '__main__':
    def main():
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        logger.setLevel(logging.DEBUG)
        
        t = tvdb( )
        r = t.search( "Dexter", "en" ).result
        for s in r:
            print s.id
        dex = r[0]

        print("Seasons--------")
        for s in dex:
            print type(s)
            for e in s[1]:
                print e

    sys.exit(main())