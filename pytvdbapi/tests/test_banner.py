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

from __future__ import absolute_import, print_function, unicode_literals
import sys
import unittest

from pytvdbapi.api import TVDB
from pytvdbapi import error
from pytvdbapi.banner import Banner


class TestBanners(unittest.TestCase):
    def setUp(self):
        self.show = self._getShow(True)

    def _getShow(self, _banners=True):
        api = TVDB("B43FF87DE395DF56", banners=_banners)
        show = api.get_series(79349, "en")  # Load the series Dexter
        show.update()

        return show

    def test_banners(self):
        """
        The banner_objects list should contain banner objects when the banner
        option is selected.
        """

        self.assertEqual(hasattr(self.show, "banner_objects"), True)

    def test_no_banners(self):
        """
        The banner_objects should be empty if the banner option
        is not selected.
        """
        show = self._getShow(False)
        self.assertEqual(len(show.banner_objects), 0)

    def test_banner_attributes(self):
        """
        The banner object should have the proper attributes.
        """

        for banner in self.show.banner_objects:
            self.assertEqual(hasattr(banner, "BannerPath"), True)
            self.assertEqual(hasattr(banner, "BannerType"), True)
            self.assertEqual(hasattr(banner, "BannerType2"), True)
            self.assertEqual(hasattr(banner, "Language"), True)
            self.assertEqual(hasattr(banner, "Rating"), True)
            self.assertEqual(hasattr(banner, "RatingCount"), True)
            self.assertEqual(hasattr(banner, "id"), True)
            self.assertEqual(hasattr(banner, "banner_url"), True)

            if banner.BannerType == "fanart":
                self.assertEqual(hasattr(banner, "Colors"), True)
                self.assertEqual(hasattr(banner, "SeriesName"), True)
                self.assertEqual(hasattr(banner, "ThumbnailPath"), True)
                self.assertEqual(hasattr(banner, "VignettePath"), True)

            elif banner.BannerType == "season":
                self.assertEqual(hasattr(banner, "Season"), True)

    def test_insensitive_attributes(self):
        """If selected, it should be possible to access the attributes in a case insensitive manner."""

        api = TVDB("B43FF87DE395DF56", banners=True, ignore_case=True)
        show = api.get_series(79349, "en")  # Load the series Dexter
        show.update()

        banner = show.banner_objects[0]
        for a in dir(banner):
            self.assertTrue(hasattr(banner, a))
            self.assertTrue(hasattr(banner, a.lower()))
            self.assertTrue(hasattr(banner, a.upper()))

    def test_iterable_banners(self):
        """
        It should be possible to iterate over the banner_objects attribute
        """
        for banner in self.show.banner_objects:
            self.assertEqual(type(banner), Banner)

    def test_invalid_banner_attributes(self):
        """
        The banner object should raise an exception when accessing an invalid
        attribute.
        """
        banner = self.show.banner_objects[0]

        self.assertRaises(error.TVDBAttributeError, banner.__getattr__, "foo")

    def test_unicode_attributes(self):
        """The attributes should be unicode on Python 2.X and str on Python 3.X"""
        _type = unicode if sys.version < '3' else str

        banner = self.show.banner_objects[0]

        for attr_name in dir(banner):
            attr = getattr(banner, attr_name)
            if type(attr) not in (float, int):
                if type(attr) in (list,):
                    for a in attr:
                        self.assertEqual(type(a), _type)
                else:
                    self.assertEqual(type(attr), _type)

    def test_banner_repr(self):
        """Banner objects should have a __repr__ attribute and it should be callable"""

        banner = self.show.banner_objects[2]

        self.assertTrue(hasattr(banner, '__repr__'))
        self.assertTrue(hasattr(banner, '__str__'))

        repr(banner)

    def test_banner_pickle(self):
        """it should be possible to pickle a banner object"""
        import pickle

        banner = self.show.banner_objects[2]

        banner_pickled = pickle.dumps(banner)
        banner_loaded = pickle.loads(banner_pickled)

        self.assertEqual(banner.BannerType, banner_loaded.BannerType)

if __name__ == "__main__":
    sys.exit(unittest.main())
