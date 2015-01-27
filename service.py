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
import utils
from requests.exceptions import Timeout, HTTPError
from trakt_library import TraktLibrary
from xbmc_library import XBMCLibrary
from sync import Sync

utils.logging_config()
logger = logging.getLogger('service')
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('pykka').setLevel(logging.WARNING)


class Monitor(xbmc.Monitor):

    def __init__(self, sync, xbmc_library):
        xbmc.Monitor.__init__(self)
        self._sync = sync
        self._xbmc_library = xbmc_library

    def onNotification(self, sender, method, data):
        data = json.loads(data)
        if method == b'VideoLibrary.OnUpdate' and 'playcount' in data:
            logger.debug("on playcount update. sender: %s data: %r" % (sender, data))
            self._on_playcount_update(data)

    def _on_playcount_update(self, data):
        media_type = data['item']['type']
        try:
            if media_type == 'movie':
                movie = self._xbmc_library.movie(data['item']['id']).get()
                if self._sync.sync_movie(movie).get() == 0:
                    logging.warning("movie did not sync %r" % movie)
                    notification("Could not sync movie")
            elif media_type == 'episode':
                episode = self._xbmc_library.episode(data['item']['id']).get()
                logger.debug("syncing episode %r " % episode)
                if self._sync.sync_episode(episode).get() == 0:
                    logging.warning("episode did not sync %r" % episode)
                    notification("Could not sync episode")
        except Timeout:
            notification("Trakt.tv did not respond.")
            traceback.print_exc()
        except HTTPError as e:
            if e.response.status_code in [401, 403]:
                notification("Authorization problem")
            elif e.response.status_code in [500, 502, 503]:
                notification("Server error")
            else:
                notification("Unexpected error")
            traceback.print_exc()
        except:
            notification("Unexpected error")
            traceback.print_exc()

    def onScanFinished(self, library):
        pass


def notification(msg):
    xbmc.executebuiltin("Notification(Trakt Sync,%s)" % msg)


def main():
    try:
        trakt_library = TraktLibrary.start().proxy()
        xbmc_library = XBMCLibrary.start().proxy()
        sync = Sync.start(xbmc_library, trakt_library).proxy()
        monitor = Monitor(sync, xbmc_library)
        monitor.waitForAbort()
    except:
        traceback.print_exc()

    logger.debug("stopping")
    pykka.ActorRegistry.stop_all()
    logger.debug("done")


if __name__ == '__main__':
    main()


