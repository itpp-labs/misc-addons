# -*- coding: utf-8 -*-
import datetime

from openerp.tools.translate import _
from openerp import tools

from openerp import exceptions
from openerp import models, fields, api


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'
    _name = 'fetchmail.server'

    _last_updated = None

    run_time = fields.Datetime(string="Launch time", compute='_run_time', store=False)

    @classmethod
    def _update_time(cls):

        cls._last_updated = tools.datetime.now()

    @api.one
    def _run_time(self):
        if not self._last_updated:

            self._last_updated = tools.datetime.now()

        src_tstamp_str = self._last_updated.strftime(tools.misc.DEFAULT_SERVER_DATETIME_FORMAT)
        src_format = tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
        dst_format = tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
        dst_tz_name = self._context.get('tz') or self.env.user.tz
        _now = tools.misc.server_to_local_timestamp(src_tstamp_str, src_format, dst_format, dst_tz_name)

        self.run_time = _now

    @api.model
    def _fetch_mails(self):

        if self._context.get('run_fetchmail_manually'):
            # if interval less than 5 seconds
            if self._last_updated and (datetime.datetime.now() - self._last_updated) < datetime.timedelta(0, 5):
                raise exceptions.Warning(_('Error'), _('Task can be started no earlier than 5 seconds.'))

        super(FetchMailServer, self)._fetch_mails()
        self._update_time()


class FetchMailImmediately(models.AbstractModel):

    _name = 'fetch_mail.imm'

    @api.model
    def get_last_update_time(self):
        res = self.env['fetchmail.server'].sudo().with_context(tz=self.env.user.tz).search([('state', '=', 'done')])
        array = [r.run_time for r in res]
        if array:
            return array[0]
        else:
            return None

    @api.model
    def run_fetchmail_manually(self):

        fetchmail_task = self.env.ref('fetchmail.ir_cron_mail_gateway_action')
        fetchmail_task_id = fetchmail_task.id
        fetchmail_model = self.env['fetchmail.server'].sudo()

        fetchmail_task._try_lock()
        fetchmail_model.with_context(run_fetchmail_manually=True)._fetch_mails()
