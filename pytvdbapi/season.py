# -*- coding: utf-8 -*-

# Copyright 2011 - 2014 Björn Larsson

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
Module to manage season instances.
"""

from collections import Sequence
import logging

from pytvdbapi import error
from pytvdbapi._compat import implements_to_string
from pytvdbapi.episode import Episode


# Module logger object
logger = logging.getLogger(__name__)

@implements_to_string
class Season(Sequence):
    """
    :raise: :exc:`pytvdbapi.error.TVDBIndexError`

    Holds all the episodes that belong to a specific season. It is possible
    to iterate over the Season to obtain the individual :class:`Episode`
    instances. It is also possible to obtain an individual episode using the
    [ ] syntax. It will raise :class:`pytvdbapi.error.TVDBIndexError` if trying
    to index an invalid episode index.

    It is possible to obtain the containing :class:`Show` instance through the
    *Season.show* attribute.

    Example::

        >>> from pytvdbapi import api
        >>> db = api.TVDB("B43FF87DE395DF56")
        >>> result = db.search("Dexter", "en")
        >>> show = result[0]

        >>> season = show[2]
        >>> len(season)  # Number of episodes in the season
        12

        >>> print(season.season_number)
        2

        >>> print(season[2].EpisodeName)
        Waiting to Exhale

        >>> for episode in season: #doctest: +ELLIPSIS
        ...     print(episode.EpisodeName)
        ...
        It's Alive!
        Waiting to Exhale
        An Inconvenient Lie
        See-Through
        ...
        Left Turn Ahead
        The British Invasion
    """

    def __init__(self, season_number, show):
        self.show, self.season_number = show, season_number
        self.episodes = dict()

    def __getitem__(self, item):
        if isinstance(item, int):
            try:
                return self.episodes[item]
            except KeyError:
                raise error.TVDBIndexError(u"Episode {0} not found".format(item))

        elif isinstance(item, slice):
            indices = sorted(self.episodes.keys())[item]  # Slice the keys
            return [self[i] for i in indices]
        else:
            raise error.TVDBValueError(u"Index should be an integer")

    def __dir__(self):  # pylint: disable=R0201
        return ['show', 'season_number']

    def __reversed__(self):
        for i in sorted(self.episodes.keys(), reverse=True):
            yield self[i]

    def __len__(self):
        return len(self.episodes)

    def __iter__(self):
        return iter(sorted(list(self.episodes.values()), key=lambda ep: ep.EpisodeNumber))

    def __str__(self):
        return u'<Season {0:03}>'.format(self.season_number)

    def __repr__(self):
        return self.__str__()

    def append(self, episode):
        """
        :param episode: The episode to append
        :type episode: :class:`Episode`

        Adds a new :class:`Episode` to the season. If an episode with the same
        EpisodeNumber already exists, it will be overwritten.
        """
        assert type(episode) in (Episode,)
        logger.debug(u"{0} adding episode {1}".format(self, episode))

        self.episodes[int(episode.EpisodeNumber)] = episode

    def find(self, key):
        """
        .. versionadded:: 0.5

        :param key: A callable taking an :class:`Episode` instance as argument and returns a boolean
        :raises: :class:`pytvdbapi.error.TypeError`
        :returns: An :class:`Episode` instance or None if no match was found

        Return the first :class:`Episode` for witch :code:`key` returns :code:`True`
        """
        try:
            return next(ep for ep in self.episodes.values() if key(ep))
        except StopIteration:  # Nothing found
            return None
        except TypeError as _error:
            raise error.TVDBTypeError("{0}".format(_error))

    def filter(self, key):
        """
        .. versionadded:: 0.5

        :param key: A callable taking an :class:`Episode` instance as argument and returns a boolean
        :raises: :class:`pytvdbapi.error.TypeError`
        :returns: list with 0 or more :class:`Episode` instances

        Return a list of all :class:`Episode` instances for witch :code:`key` returns :code:`True`
        """
        try:
            return [ep for ep in self.episodes.values() if key(ep)]
        except TypeError as _error:
            raise error.TVDBTypeError("{0}".format(_error))
