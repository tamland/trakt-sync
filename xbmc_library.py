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

import logging
import json
import pykka
from models import Movie, Episode
from utils import log


class XBMCLibrary(pykka.ThreadingActor):
    _logger = logging.getLogger('XBMCLibrary')
    _movie_properties = ['title', 'year', 'imdbnumber', 'playcount']

    def __init__(self):
        pykka.ThreadingActor.__init__(self)

    def movie(self, movieid):
        params = {
            'movieid': movieid,
            'properties': self._movie_properties
        }
        response = jsonrpc('VideoLibrary.GetMovieDetails', params)
        movie = response['result']['moviedetails']
        return _load_movie(movie)

    def episode(self, episodeid):
        params = {
            'episodeid': episodeid,
            'properties': ['season', 'episode', 'playcount', 'tvshowid'],
        }
        episode = jsonrpc('VideoLibrary.GetEpisodeDetails', params)['result']['episodedetails']
        params = {'tvshowid': episode['tvshowid'], 'properties': ['imdbnumber']}
        tvshow = jsonrpc('VideoLibrary.GetTVShowDetails', params)['result']['tvshowdetails']
        return _load_episode(episode, tvshow['imdbnumber'])

    def movies(self):
        params = {'properties': self._movie_properties}
        response = jsonrpc('VideoLibrary.GetMovies', params)
        movies = response['result'].get('movies', [])
        movies = map(_load_movie, movies)
        return [m for m in movies if m is not None]

    def episodes(self):
        params = {'properties': ['imdbnumber']}
        tvshows = jsonrpc('VideoLibrary.GetTVShows', params)['result']\
            .get('tvshows', [])
        ret = []
        for tvshow in tvshows:
            params = {
                'tvshowid': tvshow['tvshowid'],
                'properties': ['season', 'episode', 'playcount', 'lastplayed']
            }
            episodes = jsonrpc('VideoLibrary.GetEpisodes', params)['result']\
                .get('episodes', [])
            episodes = [_load_episode(ep, tvshow['imdbnumber']) for ep in episodes]
            ret.extend(episodes)
        return ret

    def update_movie_details(self, movie):
        if not movie.xbmcid or movie.playcount <= 0:
            return False
        params = {'movieid': movie.xbmcid, 'playcount': movie.playcount}
        r = jsonrpc('VideoLibrary.SetMovieDetails', params)
        return r.get('result') == 'OK'

    def update_episode_details(self, item):
        if not item.xbmcid or item.playcount <= 0:
            return False
        params = {'episodeid': item.xbmcid, 'playcount': item.playcount}
        r = jsonrpc('VideoLibrary.SetEpisodeDetails', params)
        return r.get('result') == 'OK'


def _load_movie(r):
    return Movie(
        title=r['title'],
        year=r['year'],
        imdbid=r['imdbnumber'],
        xbmcid=r['movieid'],
        playcount=r['playcount'],
    )


def _load_episode(r, tvshowid):
    return Episode(
        tvdbid=tvshowid,
        season=r['season'],
        episode=r['episode'],
        xbmcid=r['episodeid'],
        playcount=r['playcount'],
    )


def jsonrpc(method, params=None):
    if params is None:
        params = {}
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method,
        'params': params,
    }
    payload = json.dumps(payload, encoding='utf-8')
    log("payload: %r" % payload)
    try:
        import xbmc
    except:
        import requests
        response = requests.post(
            "http://localhost:8081/jsonrpc",
            data=payload,
            headers={'content-type': 'application/json'}).json()
    else:
        response = json.loads(xbmc.executeJSONRPC(payload), encoding='utf-8')

    if 'error' in response:
        log("jsonrpc error: %r" % response)
        return None
    return response
