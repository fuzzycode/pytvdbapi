Python 2.X and 3.X
==================
This section describes differences in using *pytvdbapi* in a Python 2.X environment and a Python 3.X
environment. In particular it describes the differences and changes regarding unicode handling.

Unicode Vs. Str
---------------
In python 3, the :class:`unicode` object has been removed and the standard :class:`str` type always represent
a unicode string.

Internally *pytvdbapi* works exclusively with unicode. That means that on Python 2.X all text attributes
will be of type :class:`unicode` and on Python 3 they will be of type :class:`str`,
all text attributes will be automatically converted as they are loaded.

    >>> from pytvdbapi import api
    >>> import sys
    >>> db = api.TVDB('B43FF87DE395DF56')

    >>> show = result[0]
    >>> print(show.SeriesName)
    Alarm für Cobra 11 - Die Autobahnpolizei

    >>> if sys.version < '3':
    ...     assert type(show.SeriesName) is unicode
    ... else:
    ...     assert type(show.SeriesName) is str
    ...

*pytvdbapi* attempts to convert all text parameters into unicode, that means :class:`unicode` on Python 2.X
and :class:`str` on python 3.X.

For example, both of these are valid::

    >>> from pytvdbapi import api
    >>> db = api.TVDB('B43FF87DE395DF56')

    >>> result = db.search('Alarm für cobra 11', 'de')
    >>> len(result)
    3
    >>> print(result[0])
    <Show - Alarm für Cobra 11 - Die Autobahnpolizei>


and::

    >>> result = db.search(u'Alarm für cobra 11', 'de')
    >>> len(result)
    3
    >>> print(result[0])
    <Show - Alarm für Cobra 11 - Die Autobahnpolizei>

