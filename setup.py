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
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages
import sys

from pytvdbapi.__init__ import __NAME__, version

def get_description():
    try:
        return open("README.rst").read() + '\n' + open("CHANGES.txt").read()
    except Exception:
        return "No description"

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    extra['convert_2to3_doctests'] = ['README.rst']
    author = "Björn Larsson"
else:
    author = unicode("Björn Larsson", "utf-8")

setup(
    name=__NAME__,
    version = version(),
    description='A clean, resource friendly and easy to use API for thetvdb.com',
    long_description = get_description(),
    author=author,
    author_email='develop@bjornlarsson.net',
    license = "LGPLv3",
    packages = find_packages(),
    test_suite = 'pytvdbapi.tests',
    package_data = {'' : ['data/*.xml'] },
    exclude_package_data = { '': ['./README.rst', './MANIFEST.in',
                                  './CHANGES.txt'] },
    install_requires = ['httplib2'],
    **extra
)