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

import shutil
import sys
import tempfile
import unittest
import os
from pytvdbapi import error
from pytvdbapi.loader import Loader
from pytvdbapi.tests import utils, basetest


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
        self.context = {"api_key":"B43FF87DE395DF56"}

    def tearDown(self):
        super(TestLoader, self).tearDown()
        shutil.rmtree(self.tmp)

    def test_load(self):
        """The Loader should successfully load the provided url"""
        data = utils.file_loader(os.path.join(self.path, "mirrors.xml"))

        result = self.loader.load(
            "http://www.thetvdb.com/api/%(api_key)s/mirrors.xml" % self.context)

        #Fix any new line issues to assure it does not affect the test
        data = data.replace('\r\n', '\n')
        result = result.replace('\r\n', '\n')

        self.assertEqual( data, result.encode('utf-8') )

    def test_failed_conection(self):
        """Loader should raise ConnectionError if it is not able to connect
        to the provided url
        """

        self.assertRaises( error.ConnectionError, self.loader.load,
                           "http://laba.laba")



if __name__ == "__main__":
    sys.exit(unittest.main())