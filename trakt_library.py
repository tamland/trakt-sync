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

import traceback
import pykka
from models import Movie, Episode
from trakt_session import TraktSession
from utils import log

import logging
logger = logging.getLogger(__name__)


class TraktLibrary(pykka.ThreadingActor):

    def __init__(self):
        pykka.ThreadingActor.__init__(self)
        self._trakt = TraktSession()

    def watched(self, media_type):
        if media_type == 'movies':
            return self.watched_movies()
        elif media_type == 'episodes':
            return self.watched_episodes()
        raise ValueError("Illegal media type")

    def watched_movies(self):
        movies = self._trakt.get('sync/watched/movies')
        return list(map(_load_movie, movies))

    def watched_episodes(self):
        response = self._trakt.get('sync/watched/shows')
        episodes = []
        for tvshow in response:
            for season in tvshow['seasons']:
                season_num = season['number']
                for episode in season['episodes']:
                    try:
                        episodes.append(Episode(
                            title=tvshow['show']['title'],
                            tvdbid=unicode(tvshow['show']['ids']['tvdb']),
                            season=season_num,
                            episode=episode['number'],
                            playcount=episode['plays']
                        ))
                    except KeyError:
                        logging.warning("Could not load episode.")
                        traceback.print_exc()
        return episodes

    def add_movies(self, movies):
        return self.add(movies=movies)

    def add_episodes(self, episodes):
        return self.add(episodes=episodes)

    def add(self, movies=None, episodes=None):
        if not movies and not episodes:
            raise ValueError("Nothing to add")

        payload = {}
        if movies:
            payload['movies'] = list(map(_dump_movie, movies))

        if episodes:
            payload['shows'] = _to_tvshows(episodes)

        log("trakt.add. payload %r" % payload)
        response = self._trakt.post('sync/history', json=payload)
        added = response['added'].get('movies', 0) + \
                response['added'].get('episodes', 0)
        return added

    def remove_movies(self, movies):
        return self.remove(movies=movies)

    def remove_episodes(self, episodes):
        return self.remove(episodes=episodes)

    def remove(self, movies=None, episodes=None):
        if not movies and not episodes:
            return 0
        payload = {}
        if movies:
            payload['movies'] = list(map(_dump_movie, movies))
        if episodes:
            payload['shows'] = _to_tvshows(episodes)

        log("trakt.remove. payload %r" % payload)
        response = self._trakt.post('sync/history/remove', json=payload)
        log("trakt.remove. response %r" % response)
        removed = response['deleted']['movies'] + \
                  response['deleted']['episodes']
        return removed


def _dump_movie(movie):
    return {
        'title': movie.title,
        'year': movie.year,
        'ids': {'imdb': movie.imdbid},
    }


def _load_movie(r):
    return Movie(
        title=r['movie']['title'],
        year=r['movie']['year'],
        imdbid=r['movie']['ids']['imdb'],
        playcount=r['plays'],
    )


def _to_tvshows(episodes):
    # TODO: this could be optimized
    tvshows = []
    for episode in episodes:
        tvshow = {
            'ids': {'tvdb': episode.tvdbid},
            'seasons': [
                {
                    'number': episode.season,
                    'episodes': [
                        {
                            'number': episode.episode,
                            'plays': episode.playcount,
                        }
                    ]
                }
            ]
        }
        tvshows.append(tvshow)
    return tvshows

