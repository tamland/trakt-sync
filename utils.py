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

try:
    import xbmc, xbmcaddon
    from xbmcgui import DialogProgress
except ImportError:
    class DialogProgress():
        def create(self, *args, **kwargs):
            pass
        def iscanceled(self, *args, **kwargs):
            return False
        def update(self, *args, **kwargs):
            pass


class XBMCLogHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        addon_id = xbmcaddon.Addon().getAddonInfo('id')
        prefix = b"[%s] " % addon_id
        formatter = logging.Formatter(prefix + b'%(name)s:%(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        levels = {
            logging.CRITICAL: xbmc.LOGFATAL,
            logging.ERROR: xbmc.LOGERROR,
            logging.WARNING: xbmc.LOGWARNING,
            logging.INFO: xbmc.LOGINFO,
            logging.DEBUG: xbmc.LOGDEBUG,
            logging.NOTSET: xbmc.LOGNONE,
        }
        xbmc.log(self.format(record), levels[record.levelno])

    def flush(self):
        pass


def logging_config():
    try:
        import xbmc
    except ImportError:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logger = logging.getLogger()
        logger.addHandler(XBMCLogHandler())
        logger.setLevel(logging.DEBUG)
