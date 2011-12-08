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
A module containing all the errors raised by pytvdbapi
"""

import logging

__all__ = ['pytvdbapiError', 'BadData', 'ConnectionError', 'TVDBAttributeError',
            'TVDBIndexError']

#Module level logger
logger = logging.getLogger(__name__)

class pytvdbapiError(Exception):
    """Base exception for all exceptions raised by pytvdbapi"""
    pass


class BadData(pytvdbapiError):
    pass

class ConnectionError(pytvdbapiError):
    pass

class TVDBAttributeError(pytvdbapiError):
    pass

class TVDBIndexError(pytvdbapiError):
    pass

class TVDBValueError(pytvdbapiError):
    pass