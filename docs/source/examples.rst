Examples
========
This section provides some different examples of how *pytvdbapi* can be used.

Basic Usage
-----------

Search for a show, given its name and a language::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56")
    >>> result = db.search("Dexter", "en")
    >>> show = result[0]  # If there is a perfect match, it will be the first

    >>> print(show.SeriesName)
    Dexter
    >>> print(show.FirstAired)
    2006-10-01

You can easily loop all episodes in a show::

    >>> for season in show:
    ...    for episode in season:
    ...        print(u"{0} - {1}".format(episode.EpisodeName, episode.FirstAired))  # doctest: +ELLIPSIS
    ...
    Early Cuts: Alex Timmons (Chapter 1) - 2009-10-25
    ...
    Finding Freebo - 2008-10-05
    The Lion Sleeps Tonight - 2008-10-12
    All In the Family - 2008-10-19
    Turning Biminese - 2008-10-26
    ...
    Dress Code - 2013-08-11
    Are We There Yet? - 2013-08-18
    Make Your Own Kind of Music - 2013-08-25
    Goodbye Miami - 2013-09-08
    Monkey In a Box - 2013-09-15
    Remember the Monsters? - 2013-09-22

Working with a show object
--------------------------

Basic usage::

    # You can use slicing to only get a sub set of all seasons
    >>> for season in show[2:5]:
    ...     print(season.season_number)
    ...
    2
    3
    4

    # List the total number of seasons
    # Season 0 is the "specials" season containing special episodes
    >>> len(show)
    9

    >>> print(show[2])  # Access a particular season
    <Season 002>

Access show attributes::

    >>> print(show.IMDB_ID)
    tt0773262

    >>> hasattr(show, 'foo')
    False

    >>> hasattr(show, 'Genre')
    True

    >>> getattr(show, 'foo', -1)
    -1


Working with a Season object
----------------------------

Episode access::

    >>> from pytvdbapi.error import TVDBIndexError
    >>> season = show[2]  # Grab a specific season, season 0 is the specials season

    >>> len(season)  # The number of episodes in the season
    12

    >>> try:
    ...    print(season[0])
    ... except TVDBIndexError:
    ...    # Episodes start at index 1
    ...    print('No episode at index 0')
    No episode at index 0


    >>> print(season[3])
    <Episode - S002E003>

You can use slicing to access specific episode objects::

    >>> for episode in season[3:10:2]:
    ...     print(episode.EpisodeNumber)
    ...
    4
    6
    8
    10

Access the associated show::

    >>> season.show
    <Show - Dexter>

Working with an episode object
------------------------------

Accessing episode attributes::

    >>> episode = show[2][4]
    >>> print(episode.EpisodeName)
    See-Through

    >>> hasattr(episode, 'foo')
    False

    >>> hasattr(episode, 'Director')
    True

Access the containing season::

    >>> episode.season
    <Season 002>

Searching and Filtering
-----------------------
It is possible to search and filter a show or season instance to find all episodes matching a certain
criteria.

Searching for all shows written by *Tim Schlattmann*::

    >>> episodes = show.filter(key=lambda ep: ep.Writer == 'Tim Schlattmann')
    >>> len(episodes)
    7

    >>> for ep in episodes:
    ...     print(ep.EpisodeName)
    ...
    The Dark Defender
    Turning Biminese
    Go Your Own Way
    Dirty Harry
    First Blood
    Once Upon a Time...
    Scar Tissue

Find the episode with production code 302::

    >>> episode = show.find(key=lambda ep: ep.ProductionCode==302)
    >>> print(episode.EpisodeName)
    Finding Freebo

    >>> print(episode.ProductionCode)
    302

Case insensitive attributes
---------------------------
It is possible to tell the API to ignore casing when accessing the objects dynamic attributes. If you pass
`ignore_case=True` when creating the :class:`pytvdbapi.api.TVDB` instance,
you can access the dynamically created attributes of the :class:`pytvdbapi.api.Show`,
:class:`pytvdbapi.api.Season`, :class:`pytvdbapi.api.Episode`,
:class:`pytvdbapi.actor.Actor` and :class:`pytvdbapi.banner.Banner` instances in a case insensitive manner.

Example::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56", ignore_case=True)  # Tell API to ignore case
    >>> result = db.search("Dexter", "en")
    >>> show = result[0]

    >>> print(show.seriesname)
    Dexter

    >>> hasattr(show, 'SERIESNAME')
    True
    >>> hasattr(show, 'seriesname')
    True
    >>> hasattr(show, 'sErIeSnAmE')
    True

    >>> episode = show[3][5]
    >>> print(episode.episodename)
    Turning Biminese

    >>> hasattr(episode, 'EPISODENAME')
    True
    >>> hasattr(episode, 'episodename')
    True

Working with Actor and Banner Objects
-------------------------------------
By default, the extended information for :class:`pytvdbapi.actor.Actor` and
:class:`pytvdbapi.banner.Banner` are not loaded. This is to save server resources and avoid downloading
data that is not necessarily needed. The :class:`pytvdbapi.api.Show` always contain a list of actor names.
If you *do* want to use this extra actor and banner data you can pass `actors=True` and `banners=True`
respectively when creating the :class:`pytvdbapi.api.TVDB` instance, this will cause the actors and/or
banners to be loaded for all shows. If you only want this information for some shows, you can use the
:func:`pytvdbapi.api.Show.load_actors` and
:func:`pytvdbapi.api.Show.load_banners` functions instead.

Using keyword arguments::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56", actors=True, banners=True)
    >>> result = db.search("Dexter", "en")
    >>> show = result[0]
    >>> show.update()

    >>> print(show.actor_objects[0])
    <Actor - Michael C. Hall>

Using instance functions::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56")
    >>> result = db.search("Dexter", "en")
    >>> show = result[0]

    >>> len(show.actor_objects)
    0
    >>> len(show.banner_objects)
    0

    >>> show.load_actors()  # Load actors
    >>> assert len(show.actor_objects) > 0


    >>> print(show.actor_objects[0])
    <Actor - Michael C. Hall>

    >>> show.load_banners()  # Load banners

Handle Network Issues
---------------------
This provides a more complete example of how to handle the fact that there could be something wrong with
the connection to the backend, or the backend could be malfunctioning and return invalid data that we can
not work with.


>>> from pytvdbapi import api
>>> from pytvdbapi.error import ConnectionError, BadData, TVDBIndexError
>>> db = api.TVDB("B43FF87DE395DF56")

>>> try:
...     result = db.search("Dexter", "en")  # This hits the network and could raise an exception
...     show = result[0]  # Find the show object that you want
...     show.update()  # this loads the full data set and could raise exceptions
... except TVDBIndexError:
...     # The search did not generate any hits
...     pass
... except ConnectionError:
...     # Handle the fact that the server is not responding
...     pass
... except BadData:
...     # The server responded but did not provide valid XML data, handle this issue here,
...     # maybe by trying again after a few seconds
...     pass
... else:
...     # At this point, we should have a valid show instance that we can work with.
...     name = show.SeriesName

