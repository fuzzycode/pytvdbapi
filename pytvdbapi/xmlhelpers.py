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
A helper module for parsing a XML data.
"""

import datetime
import logging
import re
import xml.etree.ElementTree as ET

try:
    from xml.etree.ElementTree import ParseError
except ImportError:
    # For Python 2.6
    from xml.parsers.expat import ExpatError as ParseError

from pytvdbapi import error

__all__ = ['generate_tree', 'parse_xml']

#Module level logger object
logger = logging.getLogger(__name__)  # pylint: disable=C0103


def generate_tree(xml_data):
    """Converts the raw xml data into an element tree"""

    try:
        tree = ET.fromstring(xml_data)
    except ParseError:
        raise error.BadData("Invalid XML data passed")

    return tree


def parse_xml(etree, element):
    """
    :param etree:
    :param element:
    :return: A list of dictionaries containing the data of the format tag:value

    Parses the element tree for elements of type *element* and converts the
    data into a dictionary.

    It will attempt some attempts to convert the data into native Python
    types. The following conversions will be applied.

      * yyyy-mm-dd will be converted into a datetime.date object.
      * Integers will be converted to int
      * Floats will be converted to float
      * Lists separated by | will be converted into a list. Eg. |foo|bar|
      will be converted into ['foo', 'bar']. Note that even if there is only
      one element it will be converted into a one element list.
    """

    logger.debug("Parsing element tree for {0}".format(element))

    _list = list()
    for item in etree.findall(element):
        data = dict()
        for child in list(item):
            tag, value = child.tag, child.text

            if value:
                value = value.strip()
            else:
                value = ""

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
    logger.debug("Found {0} element".format(len(_list)))
    return _list
