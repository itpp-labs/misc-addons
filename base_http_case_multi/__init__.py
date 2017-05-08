# -*- coding: utf-8 -*-
import json
import os
import logging

import openerp
from openerp.tests.common import HttpCase, PORT, get_db_name

_logger = logging.getLogger(__name__)


class HttpCaseMulti(HttpCase):

    def phantom_js_multi(self, sessions, commands, timeout=60, **kw):
        """check doc/index.rst for documentation"""
        for sname, sdata in sessions.items():
            session = openerp.http.root.session_store.new()
            session.db = get_db_name()
            openerp.http.root.session_store.save(session)
            sdata.setdefault('session_id', session.sid)
            sdata.setdefault('password', sdata.get('login'))

        options = {
            'port': PORT,
            'db': get_db_name(),
            'sessions': sessions,
            'commands': commands,
            'session_id': self.session_id,
        }

        options.update(kw)
        phantomtest = os.path.join(os.path.dirname(__file__), 'phantomtest.js')
        cmd = ['phantomjs', phantomtest, json.dumps(options)]

        self.phantom_run(cmd, timeout)
