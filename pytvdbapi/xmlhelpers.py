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
A helper module for parsing XML data.
"""

import datetime
import logging
import re
import xml.etree.ElementTree as eTree

try:
    from xml.etree.ElementTree import ParseError  # pylint: disable=E0611
except ImportError:
    # For Python 2.6
    from xml.parsers.expat import ExpatError as ParseError

from pytvdbapi import error
from pytvdbapi._compat import make_bytes, make_unicode

__all__ = ['generate_tree', 'parse_xml']

#Module level logger object
logger = logging.getLogger(__name__)


def generate_tree(xml_data):
    """
    :param xml_data: The string xml data to generate the tree from

    :return: A new ElementTree
    :raise: :class:`pytvdbapi.error.BadData`

    Converts the xml data into an element tree
    """
    try:
        return eTree.fromstring(make_bytes(xml_data, 'utf-8'))
    except ParseError:
        raise error.BadData(u"Bad XML data received")


def parse_xml(etree, element):
    """
    :param etree:
    :param element:
    :return: A list of dictionaries containing the data of the format tag:value

    Parses the element tree for elements of type *element* and converts the
    data into a dictionary.

    It will attempt to convert the data into native Python
    types. The following conversions will be applied.

      * yyyy-mm-dd will be converted into a datetime.date object.
      * Integers will be converted to int
      * Floats will be converted to float
      * Lists separated by | will be converted into a list. Eg. |foo|bar|
      will be converted into ['foo', 'bar']. Note that even if there is only
      one element it will be converted into a one element list.
    """

    logger.debug(u"Parsing element tree for {0}".format(element))

    _list = list()
    for item in etree.findall(element):

        data = dict()
        for child in list(item):
            tag, value = child.tag, make_unicode(child.text)

            if value:
                value = value.strip()
            else:
                value = u""

            try:  # Try to format as a datetime object
                value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                if '|' in value:  # Split piped values into a list
                    value = value.strip("|").split("|")
                    value = [s.strip() for s in value]
                else:
                    if re.match(r"^\d+\.\d+$", value):  # Convert float
                        value = float(value)
                    elif re.match(r"^\d+$", value):  # Convert integer
                        value = int(value)

            data[tag] = value
        _list.append(data)
    logger.debug(u"Found {0} element(s)".format(len(_list)))
    return _list
