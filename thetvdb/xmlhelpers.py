# -*- coding: utf-8 -*-

# Copyright 2011 Björn Larsson

# This file is part of thetvdb.
#
# thetvdb is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# thetvdb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with thetvdb.  If not, see <http://www.gnu.org/licenses/>.

import logging
import xml.etree.ElementTree as etree
from thetvdb import error

__all__ = ['generate_tree', 'parse_xml']

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler()) 

def generate_tree( xml_data, root = None ):
    """Converts the raw xml data into an element tree"""

    try:
        tree = etree.fromstring( xml_data )
    except etree.ParseError:
        raise error.BadData("Invalid XML data passed")

    if root:
        return tree.find(root)
    else:
        return tree


def parse_xml(etree, element):
    """

    :param etree:
    :param element:
    :return:
    """

    logger.debug("Parsing element tree for {0}".format(element))

    _list = list()
    for item in etree.findall( element ):
        _list.append( { i.tag:i.text for i in item.getchildren() } )

    logger.debug("Found {0} element".format(len(_list)))
    return _list