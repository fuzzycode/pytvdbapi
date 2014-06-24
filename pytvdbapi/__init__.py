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

"""
A clean, resource friendly and easy to use API for thetvdb.com_.

.. _thetvdb.com: http://thetvdb.com
"""

import logging
try:
    from logging import NullHandler  # pylint: disable=E0611
except ImportError:
    from pytvdbapi.backport import NullHandler

__VERSION__ = (0, 5, 0)
__NAME__ = 'pytvdbapi'
__EMAIL__ = 'develop@bjornlarsson.net'


def version():
    """Returns the version as a string"""
    return '.'.join([str(d) for d in __VERSION__])

# Make sure that we have a null handler on the base logger for the package
logging.getLogger(__name__).addHandler(NullHandler())
