# -*- coding: utf-8 -*-
import datetime
import psycopg2

from openerp.osv import orm
from openerp.tools.translate import _

from openerp import exceptions

from openerp.tools.safe_eval import safe_eval
from openerp import models, fields, api


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'
    _name = 'fetchmail.server'

    _last_updated = None

    run_time = fields.Char(string="Launch time", compute='_run_time', store=False)

    @classmethod
    def _update_time(cls):
        cls._last_updated = datetime.datetime.now()

    @api.one
    def _run_time(self):
        if self._last_updated:
            self.run_time = str(int((datetime.datetime.now() - self._last_updated).total_seconds() / 60))
        else:
            self._last_updated = datetime.datetime.now()
            self.run_time = '0'

    @api.model
    def _fetch_mails(self):

        if self._context.get('run_fetchmail_manually'):
            if self._last_updated and (datetime.datetime.now() - self._last_updated) < datetime.timedelta(0,5):
                raise exceptions.Warning( _('Error'), _('Task can be started no earlier than 5 seconds.'))

        super(FetchMailServer, self)._fetch_mails()
        self._update_time()


class FetchMailImmediately(models.AbstractModel):

    _name = 'fetch_mail.imm'

    @api.model
    def get_last_update_time(self):
        return self.env['fetchmail.server'].sudo().search([]).run_time

    @api.model
    def run_fetchmail_manually(self):

        fetchmail_task = self.env.ref('fetchmail.ir_cron_mail_gateway_action')
        fetchmail_task_id = fetchmail_task.id
        fetchmail_model = self.env['fetchmail.server'].sudo()

        fetchmail_task._try_lock()
        fetchmail_model.with_context(run_fetchmail_manually=True)._fetch_mails()
