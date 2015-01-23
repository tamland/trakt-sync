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

import json
import requests

try:
    import xbmc
    from xbmcgui import DialogProgress
except ImportError:
    class DialogProgress():
        def create(self, *args, **kwargs):
            pass
        def iscanceled(self, *args, **kwargs):
            return False
        def update(self, *args, **kwargs):
            pass


def log(msg):
    try:
        import xbmc
    except:
        print("%r" % msg)
    else:
        xbmc.log("[service.trakt.sync] %r" % msg, xbmc.LOGDEBUG)
