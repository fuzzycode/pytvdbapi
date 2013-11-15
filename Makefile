# -*- coding: utf-8 -*-

# Copyright 2011 - 2013 Björn Larsson

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

# A helper file to make common tasks a little bit easier

.PHONY: docs clean-docs upload-docs upload tox test coverage

clean-docs:
	@(cd docs; make clean; cd ..)

docs:
	@(python setup.py build_sphinx)

view-docs: docs
	open docs/build/html/index.html

upload-docs: clean-docs docs
	@(python setup.py upload_sphinx)

upload: tox clean-docs docs
	@(python setup.py sdist upload -r PyPI)

upload-test:
	@(python setup.py sdist upload -r PyPI-test)

tox:
	tox

test:
	python setup.py test

coverage:
	coverage run --source=pytvdbapi setup.py test; coverage report -m