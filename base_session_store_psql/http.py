# -*- coding: utf-8 -*-
import logging

import odoo
from odoo.tools.func import lazy_property

from .sessionstore import PostgresSessionStore

_logger = logging.getLogger(__name__)


class RootTkobr(odoo.http.Root):

    @lazy_property
    def session_store(self):
        # Setup http sessions
        _logger.debug('HTTP sessions stored in Postgres')
        return PostgresSessionStore(session_class=odoo.http.OpenERPSession)


root = RootTkobr()
odoo.http.root.session_store = root.session_store
