pytvdbapi - A python API for thetvdb.com
========================================
|statusimage| |coverageimage| |pypiimage|

**pytvdbapi** is a python API for thetvdb.com_ online database for tv-shows.
The API is designed to be as easy and intuitive as possible to use.

The API is designed to respect the functionality of thetvdb.com_ as far as
possible.

Key Features
------------
  * A clean and easy to use interface
  * A well documented API
  * Support for Python 2.6, 2.7, 3.3 and 3.4
  * Thoroughly tested against all supported versions.


Dependencies
============
**pytvdbapi** depends on the following packages to function.

  * `httplib2 <http://code.google.com/p/httplib2/>`_

Install
=======
The easiest and recommended way to install **pytvdbapi** is to use pip_::

    $pip install pytvdbapi

Depending on your platform, you may need root permission to execute the above
commands.


ArchLinux
----------
Tobias Röttger is kindly maintaining an ArchLinux package of **pytvdbapi** that
can be found `here <https://aur.archlinux.org/packages.php?ID=58697>`_.

Usage
=====
To use the API you should apply for an API key for your particular application.
An API key can be obtained for free from thetvdb.com_. These are some of the things you
can do with **pytvdbapi**.

Create a db instance::

    >>> from pytvdbapi import api
    >>> db = api.TVDB('B43FF87DE395DF56')

Search for a show name::

    >>> result = db.search('Dexter', 'en')
    >>> len(result)
    1


Obtain a show instance and access the data::

    >>> show = result[0]
    >>> print(show.SeriesName)
    Dexter

    >>> len(show)  # List the number of seasons of the show, season 0 is the specials season
    9

Access individual seasons::

    >>> season = show[1]
    >>> len(season)  # List the number of episodes in the season, they start at index 1
    12
    >>> print(season.season_number)
    1

Access an episode within the season::

    >>> episode = season[2]
    >>> print(episode.EpisodeNumber)
    2
    >>> print(episode.EpisodeName)
    Crocodile

Documentation
=============
The documentation for **pytvdbapi** is hosted at http://packages.python.org/pytvdbapi/ and there is a
version over at `Readthedocs <http://pytvdbapi.readthedocs.org/en/latest/>`__.

Known Issues
============
  * **pytvdbapi** only works with Python 2.6, 2.7, 3.3 and 3.4
    **NOT 3.0, 3.1 or 3.2**.
  * **pytvdbapi** does currently **NOT** support the use of Proxy Servers.

Bugs
====
If you find any bug or want to request a new feature to the API, please use
the `issue tracker <https://github.com/fuzzycode/pytvdbapi/issues>`_
associated with the project.

Try to be as detailed as possible when filing a bug, preferably providing a
patch or a test case illustrating the issue.

Contact
=======
To get in contact with me, you can send me an email at
develop@bjornlarsson.net or you can follow me on twitter
`@fuzzycode <https://twitter.com/#!/fuzzycode>`__

License
=======
**pytvdbapi** is released under the `LGPL 3 <http://opensource.org/licenses/LGPL-3.0>`__ license. See the
LICENSE.txt file for more details.




.. |statusimage| image:: https://travis-ci.org/fuzzycode/pytvdbapi.png?branch=master
    :target: https://travis-ci.org/fuzzycode/pytvdbapi
.. |coverageimage|  image:: https://coveralls.io/repos/fuzzycode/pytvdbapi/badge.png
    :target: https://coveralls.io/r/fuzzycode/pytvdbapi
.. |pypiimage| image:: https://pypip.in/v/pytvdbapi/badge.png
    :target: https://crate.io/packages/pytvdbapi/


.. _thetvdb.com: http://thetvdb.com
.. _PyPI: http://pypi.python.org/pypi
.. _pip: https://pip.pypa.io/en/latest/index.html
