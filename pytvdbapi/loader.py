# -*- coding: utf-8 -*-

# Copyright 2011 - 2014 Björn Larsson

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
A module providing the default loader to use to load urls.
"""

import logging
import os
import zipfile
from io import BytesIO

import httplib2

from pytvdbapi import error


# Module logger object
logger = logging.getLogger(__name__)


class Loader(object):
    """
    An object for loading data from a provided url.
    Uses httplib2 to do the heavy lifting.
    """

    def __init__(self, cache_path, timeout=None):
        self.http = httplib2.Http(cache=os.path.abspath(cache_path),
                                  timeout=timeout)

    def load(self, url, cache=True):
        """
        :param url: The URL to be loaded
        :param cache: Optional. Set if the cache should be ignored or not.
        :return: A file like object representing the loaded file content
        :raise: ConnectionError if the url could not be loaded

        """

        logger.debug(u"Loading data from {0}".format(url))

        header = dict()
        if not cache:
            logger.debug(u"Ignoring cached data.")
            header['cache-control'] = u'no-cache'

        try:
            response, content = self.http.request(url, headers=header)
        except (httplib2.RelativeURIError, httplib2.ServerNotFoundError):
            raise error.ConnectionError(u"Unable to connect to {0}".format(url))

        if response.status in [404]:
            raise error.TVDBNotFoundError(u"Data not found")
        elif response.status not in [200, 304]:  # pragma: no cover
            raise error.ConnectionError(u"Bad status returned from server. {0}".format(response.status))

        if response['content-type'] == "application/zip":
            zip_file = zipfile.ZipFile(BytesIO(content))
            filename = os.path.splitext(os.path.basename(url))[0]
            return zip_file.open('{0}.xml'.format(filename))
        else:
            return BytesIO(content)
