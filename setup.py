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

from distutils.core import setup
from thetvdb.__init__ import __VERSION__, __NAME__, __AUTHOR__, __EMAIL__

def get_description():
    try:
        return open("README.rst").read() + '\n' + open('CHANGES.txt').read()
    except Exception:
        return "No description"

setup(
    name = __NAME__,
    version = '.'.join([str(d) for d in __VERSION__]),
    author = __AUTHOR__,
    author_email = __EMAIL__,
    packages = ['thetvdb'],
    url = 'https://github.com/fuzzycode/thetvdb',
    download_url = 'https://github.com/fuzzycode/thetvdb/downloads',
    license = "LGPLv3",
    keywords = ['thetvdb', 'tvdb', 'tv', 'episodes', 'API'],
    description = "A clean and easy to use API for the thetvdb.com service.",
    install_requires = ['httplib2'],
    long_description = get_description(),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Internet",
    ]
)