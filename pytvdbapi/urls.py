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
URL configuration module. Store all URLs needed to access the backend service
"""

# pylint: disable=C0103

# URL templates used for loading the data from thetvdb.com
mirrors = u"http://www.thetvdb.com/api/{api_key}/mirrors.xml"
time = u"http://www.thetvdb.com/api/Updates.php?type=none"
search = u"http://www.thetvdb.com/api/GetSeries.php?seriesname={series}&language={language}"
series = u"{mirror}/api/{api_key}/series/{seriesid}/all/{language}.zip"
episode = u"{mirror}/api/{api_key}/episodes/{episodeid}/{language}.xml"
actors = u"{mirror}/api/{api_key}/series/{seriesid}/actors.xml"
banners = u"{mirror}/api/{api_key}/series/{seriesid}/banners.xml"

default_order = u"{mirror}/api/{api_key}/series/{seriesid}/default/{seasonnumber}/{episodenumber}/{" \
                u"language}.xml"
dvd_order = u"{mirror}/api/{api_key}/series/{seriesid}/dvd/{seasonnumber}/{episodenumber}/{" \
            u"language}.xml"
absolute_order = u"{mirror}/api/{api_key}/series/{seriesid}/absolute/{absolutenumber}/{language}.xml"

imdbid = u"{mirror}/api/GetSeriesByRemoteID.php?imdbid={imdbid}&language=en"
zap2itid = u"{mirror}/api/GetSeriesByRemoteID.php?language=en&zap2it={zap2itid}"
# Language is deprecated and not used, it make no difference what value is provided

airdate = u"{mirror}/api/GetEpisodeByAirDate.php?apikey={api_key}&seriesid={seriesid}&" \
          u"airdate={airdate}&language={language}"
