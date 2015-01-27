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
from itertools import chain

import logging
import pykka
from utils import DialogProgress

logger = logging.getLogger(__name__)


class Sync(pykka.ThreadingActor):
    def __init__(self, xbmc_library, trakt_library):
        pykka.ThreadingActor.__init__(self)
        self._xbmc_library = xbmc_library
        self._trakt_library = trakt_library

    def sync_movie(self, movie):
        return self._sync(movie, 'movies')

    def sync_episode(self, episode):
        return self._sync(episode, 'episodes')

    def _sync(self, item, media_type):
        if item.playcount > 0:
            # FIXME: this is very inefficient, but trakt will add duplicates if already watched
            watched = self._trakt_library.watched(media_type).get()
            watched = [x for x in watched if x.id == item.id]
            if len(watched) > 0:
                added = self._trakt_library.add(**{media_type: [item]}).get()
                logger.debug("added %s items (%s)" % (added, item))
                return added

            logger.debug("already watched (%s)" % item)
            return 1
        else:
            removed = self._trakt_library.remove(**{media_type: [item]}).get()
            logger.debug("removed %s items (%s)" % (removed, item))
            return removed


def sync_watched(xbmc_library, trakt_library, progress=None):
    if progress is None:
        progress = DialogProgress()
    progress.create("Trakt sync")

    # Fetch data
    progress.update(0, "Downloading info from trakt and kodi..")
    trakt_movies = trakt_library.watched_movies()
    trakt_episodes = trakt_library.watched_episodes()
    local_movies = xbmc_library.movies()
    local_episodes = xbmc_library.episodes()

    logger.debug("loaded %d local episodes" % (len(local_movies.get()) + len(local_episodes.get())))
    logger.debug("loaded %d trakt episodes" % (len(trakt_movies.get()) + len(trakt_episodes.get())))

    # Compute diffs
    mov_need_update_local, mov_need_update_trakt = _diff(
        local_movies.get(), trakt_movies.get())

    ep_need_update_local, ep_need_update_trakt = _diff(
        local_episodes.get(), trakt_episodes.get())

    del local_movies
    del local_episodes
    del trakt_movies
    del trakt_episodes

    if progress.iscanceled():
        return
    progress.update(50, "Updating info..")

    # Upload info
    added = trakt_library.add(
        movies=mov_need_update_trakt,
        episodes=ep_need_update_trakt)

    updated_movies = map(xbmc_library.update_movie_details, mov_need_update_local)
    updated_episodes = map(xbmc_library.update_episode_details, ep_need_update_local)

    # Get results
    needed_adding = len(mov_need_update_trakt) + len(ep_need_update_trakt)
    added = added.get()
    updated = chain(map(lambda x: x.get(), updated_movies),
                    map(lambda x: x.get(), updated_episodes))

    logger.debug("added %d of %d items to trakt." % (added, needed_adding))
    logger.debug("updated %d of %d library items." % (sum(updated), len(updated)))

    progress.update(100, "Done.")
    return added == needed_adding and sum(updated) == len(updated)


def _group_movies(local_movies, trakt_movies):
    groups = {}
    for movie in local_movies:
        assert movie is not None
        groups[movie.id] = (movie, None)
    for movie in trakt_movies:
        assert movie is not None
        other = groups.get(movie.id, [None])[0]
        groups[movie.id] = (other, movie)
    return groups


def _diff(local_movies, trakt_movies):
    items = _group_movies(local_movies, trakt_movies)

    need_update_local = [t for l, t in items.values()
                         if l is not None and t is not None
                         and l.playcount == 0 and t.playcount > 0]

    need_update_trakt = [l for l, t in items.values()
                         if t is None and l.playcount > 0]

    # FIXME:
    for item in need_update_local:
        item.xbmcid = items[item.id][0].xbmcid

    logger.debug("need update local: %d" % len(need_update_local))
    for m in need_update_local:
        logger.debug(m)
    logger.debug("need update trakt: %d" % len(need_update_trakt))
    for m in need_update_trakt:
        logger.debug(m)

    return need_update_local, need_update_trakt
