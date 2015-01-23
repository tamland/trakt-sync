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

from ConfigParser import ConfigParser

try:
    import xbmcaddon
except ImportError:

    class Config(object):
        _file_name = 'trakt.conf'

        def __init__(self):
            self._config = ConfigParser()
            self._config.read(self._file_name)
            self.username = self._config.get('trakt', 'username')
            self.password = self._config.get('trakt', 'password')

        @property
        def session_token(self):
            return self._config.get('trakt', 'session_token')

        @session_token.setter
        def session_token(self, value):
            self._config.set('trakt', 'session_token', value)
            with open(self._file_name, 'wb') as f:
                self._config.write(f)

else:

    class Config(object):
        def __init__(self):
            self._addon = xbmcaddon.Addon()

        @property
        def username(self):
            return self._addon.getSetting('username')

        @property
        def password(self):
            return self._addon.getSetting('password')

        @property
        def session_token(self):
            return self._addon.getSetting('session.token')

        @session_token.setter
        def session_token(self, value):
            self._addon.setSetting('session.token', value)



