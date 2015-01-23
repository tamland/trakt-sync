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
import logging
import traceback
import pykka
import xbmc
from trakt_library import TraktLibrary
from utils import log
from xbmc_library import XBMCLibrary
from sync import Sync

logging.basicConfig(level=logging.DEBUG)


class Monitor(xbmc.Monitor):
    def __init__(self, sync, xbmc_library):
        xbmc.Monitor.__init__(self)
        self._sync = sync
        self._xbmc_library = xbmc_library

    def onNotification(self, sender, method, data):
        data = json.loads(data)
        log("sender: %s method: %s data: %r" % (sender, method, data))

        if method == b'VideoLibrary.OnUpdate' and 'playcount' in data:
            media_type = data['item']['type']
            if media_type == 'movie':
                movie = self._xbmc_library.movie(data['item']['id']).get()
                log("Monitor: %r" % movie)
                self._sync.sync_movie(movie)
            elif media_type == 'episode':
                episode = self._xbmc_library.episode(data['item']['id']).get()
                self._sync.sync_episode(episode)

    def onScanFinished(self, library):
        pass


def main():
    try:
        trakt_library = TraktLibrary.start().proxy()
        xbmc_library = XBMCLibrary.start().proxy()
        sync = Sync.start(xbmc_library, trakt_library).proxy()
        monitor = Monitor(sync, xbmc_library)
        monitor.waitForAbort()
    except:
        traceback.print_exc()

    log("stopping")
    pykka.ActorRegistry.stop_all()
    log("done")


if __name__ == '__main__':
    main()


