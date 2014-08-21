.. -*- coding: utf-8 -*-

:mod:`api` Module
==================

.. automodule:: pytvdbapi.api

Languages
---------

.. autoclass:: pytvdbapi.api.Language
    :members:
    :show-inheritance:

.. autofunction:: pytvdbapi.api.languages


Show, Season and Episode Representation
---------------------------------------

.. autoclass:: pytvdbapi.api.Show
    :members:

.. autoclass:: pytvdbapi.api.Season
    :members:

.. autoclass:: pytvdbapi.api.Episode
    :members:

API Access
----------
.. autoclass:: pytvdbapi.api.Search
    :members:

.. autoclass:: pytvdbapi.api.TVDB(api_key, **kwargs)

    .. These are all hidden behind decorators, so we have to add them explicitly here

    .. automethod:: pytvdbapi.api.TVDB.search(show, language, cache=True)
    .. automethod:: pytvdbapi.api.TVDB.get_series(series_id, language, id_type='tvdb', cache=True)
    .. automethod:: pytvdbapi.api.TVDB.get_episode(self, language, method="id", cache=True, **kwargs)
    .. automethod:: pytvdbapi.api.TVDB.get_episode_by_air_date(self, series_id, air_date, cache=True)