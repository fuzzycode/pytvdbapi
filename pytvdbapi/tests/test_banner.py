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

from __future__ import absolute_import, print_function, unicode_literals
import sys
import unittest

from pytvdbapi.api import TVDB
from pytvdbapi import error
from pytvdbapi.banner import Banner

class TestBanners(unittest.TestCase):
    def _getShow(self, _banners=True):
        api = TVDB("B43FF87DE395DF56", banners=_banners)
        show = api.get(79349, "en")  # Load the series Dexter
        show.update()

        return show

    def test_banners(self):
        """
        The banner_objects list should contain banner objects when the banner
        option is selected.
        """
        show = self._getShow()

        self.assertEqual(hasattr(show, "banner_objects"), True)

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
        show = self._getShow()

        for banner in show.banner_objects:
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

                self.assertEqual(len(dir(banner)), 12)

            elif banner.BannerType == "season":
                self.assertEqual(hasattr(banner, "Season"), True)

                self.assertEqual(len(dir(banner)), 9)
            else:  # poster type
                self.assertEqual(len(dir(banner)), 8)

    def test_iterable_banners(self):
        """
        It should be possible to iterate over the banner_objects attribute
        """
        show = self._getShow()

        for banner in show.banner_objects:
            self.assertEqual(type(banner), Banner)

    def test_banner_representation(self):
        """
        The banner representation should be properly formatted.
        """
        show = self._getShow()
        banner = show.banner_objects[0]

        self.assertEqual(banner.__repr__(), "<Banner>")

    def test_invalid_banner_attributes(self):
        """
        The banner object should raise an exception when accessing an invalid
        attribute.
        """
        show = self._getShow()
        banner = show.banner_objects[0]

        self.assertRaises(error.TVDBAttributeError, banner.__getattr__, "foo")

if __name__ == "__main__":
    sys.exit(unittest.main())