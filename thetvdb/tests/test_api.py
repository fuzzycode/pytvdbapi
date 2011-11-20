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

import sys
import unittest
import datetime
from thetvdb import error
import thetvdb
from thetvdb.api import tvdb

from thetvdb.tests import basetest


def _load_show(show):
    """Helper function to load a show show from server"""
    api = tvdb("B43FF87DE395DF56")

    search = api.search(show, "en")
    return search[0]

class TestApi(basetest.TheTVDBTest):
    """
    These tests involve loading data from a remote server. This is far from
    ideal as the test results ends up being influenced by network
    connectivity and availability of the remote service.

     An effort should be made to change this in order for the tests to
     function reliably also when not connected.
    """
    def setUp(self):
        super(TestApi, self).setUp()

    def test_search(self):
        """It should be possible to search for shows"""
        api = tvdb("B43FF87DE395DF56")
        search = api.search("dexter", "en")

        self.assertEqual(len(search), 2)

        search = api.search("scrubs", "en")
        self.assertEqual(len(search), 2)

    def test_case_insensitive(self):
        """The test should be case insensitive"""
        api = tvdb("B43FF87DE395DF56")
        search = api.search("DeXtEr", "en")

        self.assertEqual(len(search), 2)

    def test_seasons(self):
        """The seasons should function properly"""
        friends = _load_show("friends")

        self.assertEqual(len(friends), 11)

    def test_iterate_show(self):
        """It should be possible to iterate over the show to get all seasons"""
        friends = _load_show("friends")

        count = 0
        for s in friends:
            count += 1
            #self.assertEqual(type(s), thetvdb.api.Episode)
            #TODO: Fix this test

        self.assertEqual(count, 11)

    def test_invalid_season_index(self):
        """Show should raise TVDBIndexError if trying to access invalid
        season indexes"""
        friends = _load_show("friends")

        self.assertRaises(error.TVDBIndexError, friends.__getitem__, -1)
        self.assertRaises(error.TVDBIndexError, friends.__getitem__, 12)
        self.assertRaises(error.TVDBIndexError, friends.__getitem__, 100000)
        self.assertRaises(error.TVDBIndexError, friends.__getitem__, "hello")

    def test_show_attributes(self):
        """The show instance should have correct attributes"""
        friends = _load_show("friends")

    def test_invalid_show_attribute(self):
        """"""

    def test_episodes(self):
        """"""

    def test_iterate_season(self):
        """It should be possible to iterate over a season to get all episodes"""
        friends = _load_show("friends")
        season1 = friends[1]

        #TODO: Fix this test up
        #for ep in season1:
        #    self.assertEqual(type(ep), thetvdb.api.Episode)

    def test_invalid_episode_index(self):
        """The show should raise TVDBIndexError when trying to access invalid
         indexes
         """
        friends = _load_show("friends")

        self.assertRaises(error.TVDBIndexError, friends.__getitem__, -1)
        self.assertRaises(error.TVDBIndexError, friends.__getitem__, 12)
        self.assertRaises(error.TVDBIndexError, friends.__getitem__, 100)
        self.assertRaises(error.TVDBIndexError, friends.__getitem__, "foo")

    def test_episode_attributes(self):
        """Episode should have correct attributes with correct values"""
        friends = _load_show("friends")
        ep = friends[1][1]

        self.assertEqual(ep.EpisodeName, "The One Where Monica Gets A Roommate")
        self.assertEqual(ep.Rating, "7.5")
        self.assertEqual(ep.Writer, ["David Crane", "Marta Kauffman"])
        self.assertEqual(ep.FirstAired, datetime.date(year=1994, month=9, day=22))

    def test_invalid_episode_attribute(self):
        """Episode should raise TVDBAttributeError when accessing an invalid
        attribute
        """
        friends = _load_show("friends")
        ep = friends[1][1]

        self.assertRaises(error.TVDBAttributeError, ep.__getattr__, "laba_laba")
        self.assertRaises(error.TVDBAttributeError, ep.__getattr__, "foo")
        self.assertRaises(error.TVDBAttributeError, ep.__getattr__, "baar")

    def test_search(self):
        """The search object should contain valid objects when searching for
        a valid show.
        """
        api = tvdb("B43FF87DE395DF56")
        search = api.search("dexter", "en")

        self.assertEqual(len(search), 2)
        self.assertEqual(search.search, "dexter")

        _ = search[0]

    def test_iterate_search(self):
        """It should be possible to iterate over a search result"""
        api = tvdb("B43FF87DE395DF56")
        search = api.search("house", "en")

        for s in search:
            self.assertEqual(type(s), thetvdb.api.Show)


    def test_invalid_search_index(self):
        """Search should raise TVDBIndexError when trying to access an
        invalid index
        """
        api = tvdb("B43FF87DE395DF56")
        search = api.search("dexter", "en")

        self.assertRaises(error.TVDBIndexError, search.__getitem__, 2)
        self.assertRaises(error.TVDBIndexError, search.__getitem__, 5)
        self.assertRaises(error.TVDBIndexError, search.__getitem__, 100)
        self.assertRaises(error.TVDBIndexError, search.__getitem__, "foo")

if __name__ == "__main__":
    sys.exit(unittest.main())