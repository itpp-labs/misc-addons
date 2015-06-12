# -*- coding: utf-8 -*-
import psycopg2

from openerp.tools.safe_eval import safe_eval
from openerp import models, fields, api


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'
    _name = 'fetchmail.server'

    _last_updated = None

    run_time = fields.Datetime(string="Launch time", compute='_run_time')

    @classmethod
    def _update_time(cls):
        cls._last_updated = fields.Datetime.now()

    @api.one
    def _run_time(self):
        self.run_time = self._last_updated

    @api.model
    def _fetch_mails(self):
        super(FetchMailServer, self)._fetch_mails()
        self._update_time()


class FetchMailImmediately(models.Model):

    _name = 'fetch_mail.imm'

    @api.model
    def run_fetchmail_manually(self):

        fetchmail_task = self.env['ir.cron'].search([['model', '=', 'fetchmail.server']])
        fetchmail_task_id = fetchmail_task.id
        fetchmail_model = self.env['fetchmail.server']
        cr = self.env.cr

        try:
            # Try to grab an exclusive lock on the job row
            # until the end of the transaction
            cr.execute(
                """SELECT *
                   FROM ir_cron
                   WHERE id=%s
                   FOR UPDATE NOWAIT""",
                (fetchmail_task_id,), log_exceptions=False)

            # Got the lock on the job row, run its code

            fetchmail_model._fetch_mails()

        except psycopg2.OperationalError as e:
            # User friendly error if the lock could not be claimed
            if e.pgcode == '55P03':
                raise orm.except_orm(
                    _('Error'),
                    _('Another process/thread is already busy '
                      'executing this job'))
            raise