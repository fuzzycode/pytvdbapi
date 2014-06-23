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
A module for managing the doc tests for the package
"""

import glob
import os
import doctest
import unittest

import pytvdbapi


def getFiles(root, extensions, recurse=False):
    """
    Returns all files under root that end in an extension listed in extensions
    """

    result = list()

    if recurse:
        for root, dir, files in os.walk(root):
            for file in files:
                extension = os.path.splitext(file)[1]
                if extension in extensions:
                    result.append(os.path.join(root, file))
    else:
        for ext in extensions:
            p = os.path.join(root, "*{0}".format(ext))
            result += (glob.glob(p))

    return result


def getDocTests():
    """Collects the doc tests for the pytvdbapi package"""
    tests = unittest.TestSuite()

    # Find the base dir
    base_path = os.path.dirname(pytvdbapi.__file__)

    # Grab all python modules in that package
    files = glob.glob(base_path + "/*.py")

    # Add all modules in the package
    for file in files:
        module = os.path.splitext(os.path.basename(file))[0]
        tests.addTest(doctest.DocTestSuite("pytvdbapi." + module))

    return tests


def getDocumentationTests():
    """
    This aggregates tests located inside documentation files like README and
    similar.
    """
    tests = unittest.TestSuite()

    base_dir = os.path.abspath(os.path.dirname(pytvdbapi.__file__))
    exts = ['.rst', '.txt']

    base_path = os.path.abspath(os.path.join(base_dir, "../"))
    docs_path = os.path.abspath(os.path.join(base_dir, "../docs/source/"))

    files = getFiles(base_path, exts) + getFiles(docs_path, exts, True)

    tests.addTest(doctest.DocFileSuite(*files, module_relative=False))

    return tests


def additional_tests():
    """Aggregate all tests for the module"""
    tests = unittest.TestSuite()

    tests.addTest(getDocTests())
    tests.addTest(getDocumentationTests())

    return tests


if __name__ == "__main__":
    import sys
    suite = additional_tests()
    result = unittest.TestResult(sys.stdout)
    suite.run(result)

    sys.exit(len(result.errors))
