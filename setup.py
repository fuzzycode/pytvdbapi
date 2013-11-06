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

try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup

    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import sys

from pytvdbapi.__init__ import __NAME__, version

#Make sure the user has an acceptable Python version
if sys.version_info < (2, 6):
    raise SystemExit("Your Python is too old. Only Python >= 2.6 is supported.")


def get_description():
    try:
        return open("README.rst").read() + '\n' + open("CHANGES.txt").read()
    except Exception:
        return "No description"


setup(
    name=__NAME__,
    version=version(),
    description='A clean, resource friendly and easy to use API for thetvdb.com',
    long_description=get_description(),
    author="Bjoern Larsson",
    author_email='develop@bjornlarsson.net',
    url="https://github.com/fuzzycode/pytvdbapi",
    keywords="TVDB thetvdb.com API tv episodes",
    license="LGPLv3",
    packages=find_packages(),
    platforms=["any"],
    test_suite='pytvdbapi.tests',
    package_data={'': ['data/*.xml', 'data/*.cfg']},
    exclude_package_data={'': ['./MANIFEST.in']},
    install_requires=['httplib2'],
    classifiers=[f.strip() for f in """
    Development Status :: 3 - Alpha
    Intended Audience :: Developers
    Operating System :: OS Independent
    License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
    Programming Language :: Python
    Programming Language :: Python :: 2.6
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: Utilities""".splitlines() if f.strip()],
)
