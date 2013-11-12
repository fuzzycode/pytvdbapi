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

import shutil
import sys
import tempfile
import unittest

from pytvdbapi import error
from pytvdbapi.loader import Loader
from pytvdbapi.tests import basetest


class TestLoader(basetest.pytvdbapiTest):
    """tests the loader class. At the moment, this also co-tests the httplib2
     and could fail if the network connection is not working or the remote
     server is down. This is certainly not an ideal situation and I have to
     research how to change it so that httplib2 could load from disk,
     or if the tests have to start a local server to use to perform the tests.
    """

    def setUp(self):
        super(TestLoader, self).setUp()
        self.tmp = tempfile.mkdtemp()
        self.loader = Loader(self.tmp)
        self.context = {"api_key": "B43FF87DE395DF56"}

    def tearDown(self):
        super(TestLoader, self).tearDown()
        shutil.rmtree(self.tmp)

    def test_load(self):
        """The Loader should successfully load the provided url"""
        url = ("http://www.thetvdb.com/api/%(api_key)s/mirrors.xml" %
               self.context)

        # test that we can load without exceptions
        self.loader.load(url)

    def test_failed_connection(self):
        """Loader should raise ConnectionError if it is not able to connect
        to the provided url
        """

        self.assertRaises(error.ConnectionError, self.loader.load,
                          "http://laba.laba")

    def test_no_cache(self):
        """It should be possible to disable the use of cache"""

        url = ("http://www.thetvdb.com/api/%(api_key)s/mirrors.xml" %
               self.context)

        self.loader.load(url, cache=False)


if __name__ == "__main__":
    sys.exit(unittest.main())
