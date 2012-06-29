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
A module for managing the doc tests for the package
"""

import glob
import os
import pytvdbapi
import doctest
import unittest

def getDocTests():
    """Collects the doc tests for the pytvdbapi package"""
    tests = unittest.TestSuite()

    # Find the base dir
    base_path = os.path.dirname(pytvdbapi.__file__)

    # Grab all python modules in that package
    files = glob.glob(base_path + "/*.py")

    #Add all modules in the package
    for file in files:
        module = os.path.splitext(os.path.basename(file))[0]
        tests.addTest(doctest.DocTestSuite("pytvdbapi." + module))

    return tests

def additional_tests():
    """Aggregate all tests for the module"""
    tests = unittest.TestSuite()

    tests.addTest(getDocTests())

    return tests

if __name__ == "__main__":
    import sys
    suite = additional_tests()
    result = unittest.TestResult(sys.stdout)
    suite.run(result)

    sys.exit(len(result.errors))