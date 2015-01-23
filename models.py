# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Thomas Amland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals


class Movie(object):

    def __init__(self, title, year, playcount, imdbid, xbmcid=None):
        self.title = title
        self.year = year
        self.playcount = playcount
        self.imdbid = imdbid
        self.xbmcid = xbmcid

    @property
    def id(self):
        return hash(self.imdbid)

    def __repr__(self):
        return b"Movie(%r)" % self.__dict__


class Episode(object):

    def __init__(self, episode, season, tvdbid, playcount, xbmcid=None, title=None):
        if not isinstance(tvdbid, unicode):
            raise TypeError("Expected unicode was %s" % type(tvdbid))
        self.episode = episode
        self.season = season
        self.tvdbid = tvdbid
        self.title = title
        self.xbmcid = xbmcid
        self.playcount = playcount

    @property
    def id(self):
        return hash((self.tvdbid, self.season, self.episode))

    def __repr__(self):
        return b"Episode(%r)" % self.__dict__
