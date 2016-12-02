# -*- coding: utf-8 -*-
import logging

import openerp
from openerp.tools.func import lazy_property

from .sessionstore import PostgresSessionStore

_logger = logging.getLogger(__name__)


class RootTkobr(openerp.http.Root):

    @lazy_property
    def session_store(self):
        # Setup http sessions
        _logger.debug('HTTP sessions stored in Postgres')
        return PostgresSessionStore(session_class=openerp.http.OpenERPSession)


root = RootTkobr()
openerp.http.root.session_store = root.session_store
