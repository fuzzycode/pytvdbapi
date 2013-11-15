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

from __future__ import absolute_import, print_function

import sys
import unittest
import datetime

import pytvdbapi
from pytvdbapi import error
from pytvdbapi.api import TVDB
from pytvdbapi.xmlhelpers import generate_tree
from pytvdbapi.tests import basetest


def _load_show(show):
    """Helper function to load a show show from server"""
    api = TVDB("B43FF87DE395DF56")

    search = api.search(show, "en")
    return search[0]


class TestApi(basetest.pytvdbapiTest):
    """
    These tests involve loading data from a remote server. This is far from
    ideal as the test results ends up being influenced by network
    connectivity and availability of the remote service.

     An effort should be made to change this in order for the tests to
     function reliably also when not connected.
    """

    def test_type_conversion(self):
        """Data types should be properly converted"""
        friends = _load_show("friends")
        ep = friends[1][2]

        self.assertEqual(type(ep.RatingCount), int)
        self.assertEqual(type(ep.Rating), float)
        self.assertEqual(type(ep.GuestStars), list)
        self.assertEqual(type(ep.FirstAired), datetime.date)

    def test_xml_error(self):
        """
        The tree generator should raise BadData error when passed bad xml data
        """
        data = '<?xml version="1.0" encoding="UTF-8" ?>\n<data>'

        self.assertRaises(error.BadData, generate_tree, data)

    def test_ignore_case(self):
        """
        It should be possible to pass the ignore_case keyword to the api
        and access all show/season/episode attributes in a case insensitive
        way.
        """
        api = TVDB("B43FF87DE395DF56", ignore_case=True)
        search = api.search("friends", 'en')

        # Load and update the show
        show = search[0]
        show.update()

        self.assertEqual(show.IMDB_ID, show.imdb_id)
        self.assertEqual(show.ImDB_id, show.imDb_Id)

        self.assertEqual(show.seriesid, show.SERIESID)
        self.assertEqual(show.sErIeSiD, show.SeRiEsId)

        self.assertEqual(show.zap2it_id, show.Zap2It_iD)
        self.assertEqual(show.zap2it_id, show.ZAP2IT_ID)

    def test_attribute_case(self):
        """
        When ignore_case is False, all attributes should be case sensitive
        """
        api = TVDB("B43FF87DE395DF56", ignore_case=False)
        search = api.search("friends", 'en')

        # Load and update the show
        show = search[0]
        show.update()

        self.assertRaises(error.TVDBAttributeError, show.__getattr__, "ImDB_id")

    def test_cache_dir(self):
        """It should be possible to specify a custom cache directory"""
        #TODO: Implement this

    def test_version_format(self):
        """The package version string should be properly formatted"""
        import re

        _format = r'^\d{1,2}\.\d{1,2}(?:\.\d{1,2})?$'

        m = re.match(_format, pytvdbapi.version())
        self.assertNotEqual(m, None)


class TestSeason(unittest.TestCase):
    def setUp(self):
        self.friends = _load_show('friends')
        self.friends.update()

    def test_seasons(self):
        """The seasons should function properly"""

        self.assertEqual(len(self.friends), 11)

    def test_invalid_season_index(self):
        """Season should raise exception if trying to access invalid
        season indexes"""
        season1 = self.friends[1]

        self.assertRaises(error.TVDBIndexError, season1.__getitem__, -1)
        self.assertRaises(error.TVDBIndexError, season1.__getitem__, 100000)
        self.assertRaises(error.TVDBValueError, season1.__getitem__, "hello")

    def test_iterate_season(self):
        """
        It should be possible to iterate over a season to get all episodes
        """

        season1 = self.friends[1]

        for ep in season1:
            self.assertEqual(type(ep), pytvdbapi.api.Episode)

    def test_season_sort_order(self):
        """The Episodes should be sorted on the episode number when iterating
         over a season
         """

        season1 = self.friends[1]

        counter = 0
        for ep in season1:
            self.assertEqual(counter + 1, ep.EpisodeNumber)
            counter += 1

    def test_episodes(self):
        """The episodes should function properly"""

        season1 = self.friends[1]

        self.assertEqual(len(season1), 24)

    def test_index(self):
        """It should be possible to use the index method on a season"""
        season = self.friends[1]

        for i, ep in enumerate(season):
            self.assertEquals(season.index(ep), i)

    def test_count(self):
        """It should be possible to use the count method on a season."""
        season = self.friends[1]

        for ep in season:
            self.assertEquals(season.count(ep), 1)

    def test_reversed_order(self):
        """It should be possible to iterate the episodes in reversed order"""

        season = self.friends[1]
        reverse = reversed(season)
        prev = len(season) + 1

        for ep in reverse:
            self.assertTrue(prev > ep.EpisodeNumber)
            prev = ep.EpisodeNumber

    def test_slice(self):
        """It should be possible to use slice syntax on the Season"""

        season = self.friends[1]

        # Normal slice
        _range = season[2:5]
        for i, v in enumerate(range(3, 6)):
            self.assertEquals(_range[i].EpisodeNumber, v)

        # Slice with a step size
        _range = season[2:8:2]
        for i, v in enumerate(range(3, 9, 2)):
            self.assertEquals(_range[i].EpisodeNumber, v)

        # Out of range slice
        _range = season[20:30]
        for i, v in enumerate(range(21, 25)):
            self.assertEquals(_range[i].EpisodeNumber, v)

    def test_season_pickle(self):
        """It should be possible to pickle and unpickle a season"""

        import pickle

        season = self.friends[2]

        pickled_season = pickle.dumps(season)
        loaded_season = pickle.loads(pickled_season)

        self.assertTrue(loaded_season.season_number == season.season_number,
                        "Episode should keep its name attribute")

    def test_dir(self):
        """It should be possible to use dir() on a season, and it should show the right values"""
        attributes = ['show', 'season_number']

        for a in dir(self.friends[2]):
            self.assertTrue(a in attributes)


class TestShow(unittest.TestCase):
    def setUp(self):
        self.friends = _load_show('friends')
        self.friends.update()

    def test_show_dir(self):
        """
        It should be possible to call dir() on a show object.
        Before updating it should contain a sub set of attributes and after
        updating it should contain the full set of attributes.
        """

        friends = _load_show("friends")

        _before = len(dir(friends))
        friends.update()
        _after = len(dir(friends))

        self.assertTrue(_after >= _before, "Calling update should increase the number of attributes")
        self.assertTrue('actor_objects' in dir(friends), "Show should have an actor objects attribute")
        self.assertTrue('banner_objects' in dir(friends), "Show should have a banner objects attribute")
        self.assertTrue('lang' in dir(friends), "Show should have a lang attribute")
        self.assertTrue('api' in dir(friends), "Show should have an api attribute")

    def test_show_pickle(self):
        """It should be possible to pickle and unpickle a fully loaded show"""

        import pickle

        friends = _load_show("friends")

        pickled_show = pickle.dumps(friends)
        loaded_show = pickle.loads(pickled_show)

        self.assertTrue(loaded_show.SeriesName == friends.SeriesName, "Show should keep its name attribute")

    def test_iterate_show(self):
        """It should be possible to iterate over the show to get all seasons"""

        count = 0
        for s in self.friends:
            count += 1
            self.assertEqual(type(s), pytvdbapi.api.Season)

        self.assertEqual(count, 11)

    def test_show_sort_order(self):
        """The seasons should be sorted on season number when iterating over
        a show
        """

        counter = 0
        for season in self.friends:
            self.assertEqual(counter, season.season_number)
            counter += 1

    def test_show_attributes(self):
        """The show instance should have correct attributes"""
        friends = _load_show("friends")

        self.assertEqual(friends.SeriesName, "Friends")
        self.assertEqual(friends.id, 79168)

        #This should not yet be loaded so should raise an error
        self.assertRaises(
            error.TVDBAttributeError, friends.__getattr__, "Genre")

        #Load in the rest of the attributes
        friends.update()

        #Now this data should be available
        self.assertEqual(friends.Genre, ['Comedy'])

    def test_invalid_show_attribute(self):
        """
        The Show object should raise TVDBAttributeError when you try to
        access an invalid attribute
        """

        self.assertRaises(error.TVDBAttributeError, self.friends.__getattr__, "foo")
        self.assertRaises(
            error.TVDBAttributeError, self.friends.__getattr__, "baar")
        self.assertRaises(
            error.TVDBAttributeError, self.friends.__getattr__, "laba_laba")

    def test_get_actors_function(self):
        """
        It should be possible to load the actor object on the show instance.
        """
        friends = _load_show("friends")
        self.assertEquals(len(friends.actor_objects), 0,
                          "There should be no actors before calling the function.")

        friends.load_actors()

        self.assertTrue(len(friends.actor_objects) > 0,
                        "There should be actors available after loading them.")

    def test_get_banners_function(self):
        """
        It should be possible to load the banner objects on the show instance.
        """
        friends = _load_show("friends")
        self.assertEquals(len(friends.banner_objects), 0,
                          "There should be no banners before calling the function.")

        friends.load_banners()

        self.assertTrue(len(friends.banner_objects) > 0,
                        "There should be banners available after loading them.")

    def test_attribute_access(self):
        """It should be possible to use standard python functions to access attributes"""

        self.assertEquals(self.friends.SeriesName, getattr(self.friends, 'SeriesName'))
        self.assertEquals('baar', getattr(self.friends, 'foo', 'baar'))

        self.assertEquals(True, hasattr(self.friends, 'SeriesName'))
        self.assertEquals(False, hasattr(self.friends, 'foo'))

    def test_reversed_order(self):
        """It should be possible to iterate the seasons in reversed order"""

        reverse = reversed(self.friends)
        prev = len(self.friends)
        for season in reverse:
            self.assertTrue(prev > season.season_number)
            prev = season.season_number

    def test_index(self):
        """It should be possible to use the index function on the seasons"""

        for i, s in enumerate(self.friends):
            self.assertEquals(self.friends.index(s), i)

    def test_count(self):
        """It should be possible to use the count function on the seasons"""

        for s in self.friends:
            self.assertEquals(self.friends.count(s), 1)

    def test_invalid_index(self):
        """class should raise an exception if trying to use an invalid index"""

        #Non integer index
        self.assertRaises(error.TVDBValueError, self.friends.__getitem__, 'foo')

        #Index out of range
        self.assertRaises(error.TVDBIndexError, self.friends.__getitem__, 9999)

    def test_slice(self):
        """It should be possible to use slice syntax on the show"""

        # Normal slice
        _range = self.friends[2:5]
        for i, v in enumerate(range(2, 5)):
            self.assertEquals(_range[i].season_number, v)

        # Slice with a step size
        _range = self.friends[2:8:2]
        for i, v in enumerate(range(2, 8, 2)):
            self.assertEquals(_range[i].season_number, v)

        # Out of range slice
        _range = self.friends[8:20]
        for i, v in enumerate(range(8, 10)):
            self.assertEquals(_range[i].season_number, v)

    def test_unicode_attributes(self):
        """The attributes should be unicode on Python 2.X and str on Python 3.X"""
        _type = unicode if sys.version < '3' else str

        for attr_name in dir(self.friends):
            attr = getattr(self.friends, attr_name)
            if type(attr) not in (float, int, bool, datetime.date, pytvdbapi.api.TVDB):
                if type(attr) in (list,):
                    for a in attr:
                        self.assertEqual(type(a), _type,
                                         u"Attr: {0} was not {1} but {2}".format(attr_name, _type,
                                                                                 type(attr)))
                else:
                    self.assertEqual(type(attr), _type,
                                     u"Attr: {0} was not {1} but {2}".format(attr_name, _type, type(attr)))


class TestEpisode(unittest.TestCase):
    def setUp(self):
        self.friends = _load_show('friends')
        self.friends.update()

    def test_episode_dir(self):
        """It should be possible to call dir() on a episode instance"""

        ep = self.friends[3][7]

        self.assertTrue(len(dir(ep)) >= 1, "There was no info from calling dir")
        self.assertTrue('season' in dir(ep), "The episode should contain the season attribute")

    def test_episode_attributes(self):
        """Episode should have correct attributes with correct values"""
        ep = self.friends[1][1]

        self.assertEqual(
            ep.EpisodeName, "The One Where Monica Gets A Roommate")
        self.assertEqual(ep.Writer, ["David Crane", "Marta Kauffman"])
        self.assertEqual(
            ep.FirstAired, datetime.date(year=1994, month=9, day=22))

    def test_invalid_episode_attribute(self):
        """Episode should raise TVDBAttributeError when accessing an invalid
        attribute
        """
        ep = self.friends[1][1]

        self.assertRaises(
            error.TVDBAttributeError, ep.__getattr__, "laba_laba")
        self.assertRaises(error.TVDBAttributeError, ep.__getattr__, "foo")
        self.assertRaises(error.TVDBAttributeError, ep.__getattr__, "baar")

    def test_attribute_access(self):
        """It should be possible to access attributes using standard python methods"""

        ep = self.friends[1][1]

        self.assertEquals(True, hasattr(ep, 'Rating'))
        self.assertEquals(False, hasattr(ep, 'foo'))

        self.assertEquals(getattr(ep, 'foo', 'baar'), 'baar')

    def test_episode_pickle(self):
        """It should be possible to pickle and unpickle an episode"""

        import pickle

        ep = self.friends[2][3]

        pickled_ep = pickle.dumps(ep)
        loaded_ep = pickle.loads(pickled_ep)

        self.assertTrue(loaded_ep.EpisodeName == ep.EpisodeName, "Episode should keep its name attribute")

    def test_unicode_attributes(self):
        """The attributes should be unicode on Python 2.X and str on Python 3.X"""
        _type = unicode if sys.version < '3' else str
        ep = self.friends[2][3]

        for attr_name in dir(ep):
            attr = getattr(ep, attr_name)
            if type(attr) not in (float, int, datetime.date, pytvdbapi.api.Season):
                if type(attr) in (list,):
                    for a in attr:
                        self.assertEqual(type(a), _type,
                                         u"Attr: {0} was not {1} but {0}".format(attr_name,
                                                                                 _type, type(attr)))
                else:
                    self.assertEqual(type(attr), _type,
                                     u"Attr: {0} was not {1} but {0}".format(attr_name, _type, type(attr)))

    def test_repr(self):
        """It should be possible to use the __repr__ function"""
        ep = self.friends[2][3]
        repr(ep)


class TestSearch(unittest.TestCase):
    def test_invalid_search_index(self):
        """Search should raise TVDBIndexError when trying to access an
        invalid index
        """
        api = TVDB("B43FF87DE395DF56")
        search = api.search("dexter", "en")

        self.assertRaises(error.TVDBIndexError, search.__getitem__, 10)
        self.assertRaises(error.TVDBIndexError, search.__getitem__, 50)
        self.assertRaises(error.TVDBIndexError, search.__getitem__, 100)
        self.assertRaises(error.TVDBValueError, search.__getitem__, "foo")

    def test_iterate_search(self):
        """It should be possible to iterate over a search result"""
        api = TVDB("B43FF87DE395DF56")
        search = api.search("house", "en")

        for s in search:
            self.assertEqual(type(s), pytvdbapi.api.Show)

    def test_search(self):
        """It should be possible to search for shows"""
        api = TVDB("B43FF87DE395DF56")
        search = api.search("dexter", "en")

        self.assertEqual(len(search), 1)

        search = api.search("scrubs", "en")
        self.assertEqual(len(search), 2)

        search = api.search("dexter", "en")

        self.assertEqual(len(search), 1)
        self.assertEqual(search.search, "dexter")

    def test_case_insensitive(self):
        """The search should be case insensitive"""
        api = TVDB("B43FF87DE395DF56")
        search = api.search("DeXtEr", "en")

        self.assertEqual(len(search), 1)

    def test_numeric_names(self):
        """It should be possible to search for shows with all
        numeric names. E.g. 24
        """
        show = _load_show('24')

        self.assertEqual(show.FirstAired, datetime.date(2001, 11, 6))

    def test_unicode_search(self):
        """
        It should be possible to search for shows containing non ascii chars
        """

        api = TVDB("B43FF87DE395DF56")

        search = api.search(u"Alarm für cobra 11", "de")
        show = search[0]
        self.assertEqual(show[1][2].EpisodeName, u"Rote Rosen, schwarzer Tod")

        search = api.search("Alarm für cobra 11", u"de")
        show = search[0]
        self.assertEqual(show[1][2].EpisodeName, u"Rote Rosen, schwarzer Tod")

        search = api.search(u'3年B組金八先生', "zh")
        show = search[0]
        self.assertEqual(show[1][1].EpisodeName, u"3年B組金八先生")

    def test_names_with_spaces(self):
        """It should be possible to search for shows with spaces in the name"""
        api = TVDB("B43FF87DE395DF56")
        search = api.search("How I Met Your Mother", "en")

        self.assertEqual(len(search), 1)

    def test_invalid_language(self):
        """Search function should raise TVDBValueError when trying to search
        with an invalid language
        """
        api = TVDB("B43FF87DE395DF56")

        self.assertRaises(error.TVDBValueError, api.search, "dexter", "lu")


class TestGetSeries(unittest.TestCase):
    def test_get(self):
        """Provided the show id, you should be able to get the show object"""
        api = TVDB("B43FF87DE395DF56")
        show = api.get_series(79349, "en")

        self.assertEqual(show.SeriesName, "Dexter")
        self.assertEqual(show.id, 79349)

    def test_invalid_language(self):
        """
        Function should raise TVDBValueError if an invalid language is
        passed
        """

        api = TVDB("B43FF87DE395DF56")
        self.assertRaises(error.TVDBValueError, api.get_series, 79349, "foo")
        self.assertRaises(error.TVDBValueError, api.get_series, 79349, "")

    def test_invalid_id(self):
        """If the show can not be found, a TVDBValueError should be raised"""
        api = TVDB("B43FF87DE395DF56")

        self.assertRaises(error.TVDBIdError, api.get_series, 99999999999999, "en")
        self.assertRaises(error.TVDBIdError, api.get_series, "foo", "en")
        self.assertRaises(error.TVDBIdError, api.get_series, "", "en")


class TestGetEpisode(unittest.TestCase):
    def test_get_episode(self):
        """
        Provided the episode id, you should be able to
        get episode instance.
        """
        api = TVDB("B43FF87DE395DF56")
        ep = api.get_episode(308834, "en")

        self.assertEqual(ep.id, 308834)
        self.assertEqual(ep.EpisodeName, 'Crocodile')

    def test_invalid_language(self):
        """
        Function should raise TVDBValueError if an invalid language is
        passed
        """

        api = TVDB("B43FF87DE395DF56")
        self.assertRaises(error.TVDBValueError, api.get_episode, 308834, "foo")
        self.assertRaises(error.TVDBValueError, api.get_episode, 308834, "")

    def test_invalid_id(self):
        """
        If the episode can not be found, a TVDBValueError should be raised.
        """
        api = TVDB("B43FF87DE395DF56")

        self.assertRaises(error.TVDBIdError, api.get_episode, -1, "en")
        self.assertRaises(error.TVDBIdError, api.get_episode, "foo", "en")
        self.assertRaises(error.TVDBIdError, api.get_episode, "", "en")


if __name__ == "__main__":
    sys.exit(unittest.main())
