import logging
_logger = logging.getLogger(__name__)

import openerp
from openerp.tools.func import lazy_property

from .sessionstore import PostgresSessionStore

class Root_tkobr(openerp.http.Root):

    @lazy_property
    def session_store(self):
        # Setup http sessions
        _logger.debug('HTTP sessions stored in Postgres')
        return PostgresSessionStore(session_class=openerp.http.OpenERPSession)

root = Root_tkobr()
openerp.http.root.session_store = root.session_store

