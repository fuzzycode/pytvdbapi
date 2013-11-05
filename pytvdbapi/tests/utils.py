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

__all__ = ['file_loader']

# pylint: disable W0622
try:
    from io import open  # For Py 2.6 - 2.7
except ImportError:
    pass
# pylint: enable W0622


def file_loader(_file):
    """
    :param _file: Path to load
    """
    try:
        handle = open(_file, mode='rt', encoding='utf-8')
        data = handle.read()
    except IOError:
        print("Unable to open {0}".format(_file))
        data = ""
    finally:
        handle.close()

    return data
