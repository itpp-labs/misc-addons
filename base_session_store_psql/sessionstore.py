# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import pickle

from openerp import exceptions
from openerp.sql_db import db_connect
from openerp.tools import config
from openerp.http import db_list

import psycopg2

from werkzeug.contrib.sessions import SessionStore


class PostgresSessionStore(SessionStore):

    def __init__(self, session_class=None):
        super(PostgresSessionStore, self).__init__(session_class=session_class)
        # set value to avoid errors in session_gc function
        self.path = config.session_dir

    def get_cursor(self):
        db_name = config.get('log_db')
        con = db_connect(db_name)
        cr = con.cursor()
        cr.execute(
            """
            CREATE TABLE IF NOT EXISTS sessionstore (
              id varchar(40),
              data bytea
            );
            """)
        cr.commit()

        return cr

    def is_valid_key(self, key):
        with self.get_cursor() as cr:
            cr.execute("SELECT id FROM sessionstore WHERE id = %s LIMIT 1;",
                       (key,))
            return cr.rowcount == 1

    def save(self, session):
        with self.get_cursor() as cr:
            sql_data = {
                'data': psycopg2.Binary(pickle.dumps(dict(session),
                                        pickle.HIGHEST_PROTOCOL)),
                'id': session.sid,
            }

            if self.is_valid_key(session.sid):
                cr.execute(
                    """
                    UPDATE sessionstore SET data = %(data)s WHERE id = %(id)s;
                    """, sql_data)
            else:
                cr.execute(
                    """
                    INSERT INTO sessionstore (id, data)
                    VALUES (%(id)s, %(data)s);
                    """, sql_data)
            cr.commit()

    def delete(self, session):
        with self.get_cursor() as cr:
            cr.execute("DELETE FROM sessionstore WHERE id = %s;",
                       (session.sid,))

    def get(self, sid):
        with self.get_cursor() as cr:
            cr.execute(
                """
                SELECT data FROM sessionstore WHERE id = %s LIMIT 1;
                """, (sid,))

            if cr.rowcount != 1:
                return self.new()

            result = cr.fetchone()

            try:
                data = pickle.loads(result[0])
            except Exception:
                data = {}

            return self.session_class(data, sid, False)

    def list(self):
        with self.get_cursor() as cr:
            cr.execute("SELECT id FROM sessionstore;")

            return [rec[0] for rec in cr.fetchall()]
