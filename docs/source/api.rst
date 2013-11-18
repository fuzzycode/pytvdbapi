.. -*- coding: utf-8 -*-

:mod:`api` Module
==================

.. automodule:: pytvdbapi.api

Languages
----------

.. autoclass:: pytvdbapi.api.Language
    :members:
    :show-inheritance:

.. autofunction:: pytvdbapi.api.languages


Show, Season and Episode Representation
---------------------------------------

.. autoclass:: pytvdbapi.api.Show
    :members:
    :show-inheritance:

.. autoclass:: pytvdbapi.api.Season
    :members:
    :show-inheritance:

.. autoclass:: pytvdbapi.api.Episode
    :members:
    :show-inheritance:

API Access
----------
.. autoclass:: pytvdbapi.api.Search
    :members:
    :show-inheritance:

.. autoclass:: pytvdbapi.api.TVDB(api_key, **kwargs)
    :show-inheritance:

    .. These are all hidden behind decorators, so we have to add them explicitly here

    .. automethod:: pytvdbapi.api.TVDB.search(show, language, cache=True)
    .. automethod:: pytvdbapi.api.TVDB.get(series_id, language, cache=True)
    .. automethod:: pytvdbapi.api.TVDB.get_series(series_id, language, cache=True)
    .. automethod:: pytvdbapi.api.TVDB.get_episode(series_id, language, cache=True)
