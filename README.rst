pytvdbapi - A python API for thetvdb.com
========================================
|statusimage| |coverageimage| |pypiimage|

**pytvdbapi** is a python API for thetvdb.com_ online database for tv-shows.
The API is designed to be as easy and intuitive as possible to use.

The API is designed to respect the functionality of thetvdb.com_ as far as
possible. It uses caching as much as possible to reduce the workload of the
servers.

Key Features
------------
  * A clean and easy to use interface
  * A well documented API
  * Support for Python 2.6, 2.7, 3.2 and 3.3
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

To get the latest development version you can install directly from source.
Note that no guaranties are made as to the stability of the source tree::

    $pip install git+git://github.com/fuzzycode/pytvdbapi.git


ArchLinux
----------
Tobias Röttger is kindly maintaining an ArchLinux package of **pytvdbapi** that
can be found `here <https://aur.archlinux.org/packages.php?ID=58697>`_.

Usage
=====
To use the API you should apply for an API key for your particular application.
An API key can be obtained for free from thetvdb.com_. Note that the key
used in the examples is only intended for testing purposes and should not be
used for other purposes.

To search for a specific show::

    >>> from pytvdbapi import api
    >>> db = api.TVDB("B43FF87DE395DF56")
    >>> search = db.search("How I met your mother", "en")
    >>> len(search)
    1
    >>> show = search[0]
    >>> show.SeriesName
    'How I Met Your Mother'


You can index individual seasons and individual episodes using convenient
indexing::

    >>> show[1]
    <Season 001>

    >>> show[1][4]
    <Episode S001E004 - Return of the Shirt>


To list all episodes of a show::

    >>> for season in show:
    ...     for episode in season:
    ...         print(episode) #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...
    <Episode S000E001 - Robin Sparkles Music Video - Let's Go to the Mall>
    <Episode S000E002 - Robin Sparkles Music Video - Sandcastles In the Sand>
    <Episode S000E003 - Marshall's Music Video - You Just Got Slapped>
    <Episode S000E004 - Lily and Marshall's Honeymoon Videos>
    <Episode S000E005 - Barney Stinson's Video Resume>
    <Episode S000E006 - Nothing Suits Me Like A Suit>
    <Episode S000E007 - A Night With Your Mother Panel Discussion>
    <Episode S000E008 - The Beaver Song>
    <Episode S000E009 - Best Night Ever>
    <Episode S000E010 - Best Night Ever: Behind the Scenes>
    <Episode S001E001 - Pilot>
    <Episode S001E002 - Purple Giraffe>
    ...
    ...
    <Episode S007E010 - Tick Tick Tick...>
    <Episode S007E011 - The Rebound Girl>
    <Episode S007E012 - Symphony of Illumination>
    ...

Testing
=======
Testing **pytvdbapi** is really easy, just type the following from the package
root folder::

    $ python setup.py test

If all turns out all right you should see a nice and happy OK at the end.


Documentation
=============
The documentation for **pytvdbapi** is hosted at
http://packages.python.org/pytvdbapi/.
It also comes with a version of the documentation included in
*docs/build/html/*.

Known Issues
============
  * At the moment, **pytvdbapi** only works with Python 2.6, 2.7, 3.2 and 3.3,
    **NOT 3.0 or 3.1**. This is due to an
    `issue <http://code.google.com/p/httplib2/issues/detail?id=195>`_
    with httplib2 on Python 3.0, 3.1.
  * **pytvdbapi** does currently **NOT** support the use of Proxy Servers.


Bugs
====
If you find any bug or want to request a new feature to the API please use
the `issue tracker <https://github.com/fuzzycode/pytvdbapi/issues>`_
associated with the project.

Try to be as detailed as possible when filing a bug, preferably providing a
patch or a test case illustrating the issue.

Contact
=======
To get in contact with me, you can send me an email at
develop@bjornlarsson.net or you can follow me on twitter
`@fuzzycode <https://twitter.com/#!/fuzzycode>`__






.. |statusimage| image:: https://travis-ci.org/fuzzycode/pytvdbapi.png?branch=master
    :target: https://travis-ci.org/fuzzycode/pytvdbapi
.. |coverageimage|  image:: https://coveralls.io/repos/fuzzycode/pytvdbapi/badge.png
    :target: https://coveralls.io/r/fuzzycode/pytvdbapi
.. |pypiimage| image:: https://pypip.in/v/pytvdbapi/badge.png
    :target: https://crate.io/packages/pytvdbapi/



.. _thetvdb.com: http://thetvdb.com
.. _PyPI: http://pypi.python.org/pypi
.. _pip: http://www.pip-installer.org/en/latest/index.html
