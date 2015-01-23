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
import requests
from config import Config


logger = logging.getLogger(__name__)


class TraktSession(object):
    _base_url = 'https://api.trakt.tv/'
    _api_key = 'd4161a7a106424551add171e5470112e4afdaf2438e6ef2fe0548edc75924868'

    def __init__(self):
        self._config = Config()
        self._init_session()

    def _init_session(self):
        self._session = requests.Session()
        self._session.headers = {
            'content-type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': self._api_key,
            'trakt-user-login': self._config.username,
            'trakt-user-token': self._config.session_token,
        }

    def login(self):
        headers = {
            'content-type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': self._api_key,
        }
        data = {
            'login': self._config.username,
            'password': self._config.password,
        }
        response = requests.post(self._base_url + 'auth/login',
                                 headers=headers, json=data)
        response.raise_for_status()
        self._config.session_token = response.json()['token']
        self._init_session()

    def _request(self, method, endpoint, autologin=True, **kwargs):
        kwargs['timeout'] = 5
        url = self._base_url + endpoint
        response = self._session.request(method, url, **kwargs)
        if response.status_code == 401 and autologin:
            logger.info("401 Unauthorized")
            self.login()
            response = self._session.request(method, url, **kwargs)

        response.raise_for_status()
        return response.json()

    def get(self, endpoint, autologin=True, **kwargs):
        return self._request('GET', endpoint, autologin, **kwargs)

    def post(self, endpoint, autologin=True, **kwargs):
        return self._request('POST', endpoint, autologin, **kwargs)

