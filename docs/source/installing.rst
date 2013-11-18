.. -*- coding: utf-8 -*-

Getting Started
===============
About
-----
**pytvdbapi** is created to be an easy to use and intuitive Python API for the TV-Show database thetvdb.com_.
It is designed with the intention of making it easier and faster to develop applications using data
from thetvdb.com_, without having to bother about working with the raw data provided.

Installing
----------
The best and recommended way to install *pytvdbapi* is to use pip_. To install,
issue the following command in a shell::

    $ pip install pytvdbapi

Depending on on what system and where you install *pytvdbapi* you may need root privileges to perform the
above command.

Dependencies
------------
*pytvdbapi* depends on the following external packages:

  * httplib2_

If you install using the above description, the dependencies will be installed for you if you do not
already have them on your system.

Supported Versions
------------------
The following python versions are supported by *pytvdbapi*.

  * 2.6
  * 2.7
  * 3.3

It may work on other Python versions but they are not actively supported and tested against.

Known Issues
------------
The following issues/problems with *pytvdbapi* are known.

  * No support for connections through proxy servers.


.. _httplib2: http://code.google.com/p/httplib2/
.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _thetvdb.com: http://thetvdb.com