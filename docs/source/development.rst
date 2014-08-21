.. -*- coding: utf-8 -*-

Contributing
============
All forms of contributions to *pytvdbapi* are welcome, anything from improving the documentation correcting
the language or the examples to adding new features are very very welcome.

Pull requests
-------------

Bug reports/Feature requests
----------------------------
Please add all your bug reports to the official `bug tracker <https://github
.com/fuzzycode/pytvdbapi/issues>`_. Try to be as specific as possible when filing an issue,
and if possible provide a test case or steps to reproduce the issue.

Dependencies
============

Runtime
-------
*pytvdbapi* depends on the following packages to function at runtime.

 * `httplib2 <http://code.google.com/p/httplib2/>`_

Development
-----------
None of the following packages are required to run *pytvdbapi* but they will aid the development and help
maintaining and improving the quality of *pytvdbapi*.

 * `Tox <https://testrun.org/tox/latest/>`_
 * `PEP8 <http://pep8.readthedocs.org/en/latest/>`_
 * `pyLint <http://www.pylint.org/>`_
 * `coverage <http://nedbatchelder.com/code/coverage/>`_
 * `Sphinx <http://sphinx-doc.org/contents.html>`_
 * `Virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_
 * `Virtualenv Wrapper <http://virtualenvwrapper.readthedocs.org/en/latest/>`_


Testing
=======
You should verify the changes by running tox on the project to make sure that *pytvdbapi* will run without
issues on all supported versions of Python and that no PEP8 or pyLint issues are found.

You might have to install additional versions of python to make sure that tox can test against all
supported versions.

Coverage
--------
The goal of the project is to have a well tested and stable API, therefor it is important that any new code
 contributed also come with sufficient tests to assure that the amount of coverage is maintained or increased.

