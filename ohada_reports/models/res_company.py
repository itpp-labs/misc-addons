# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import requests
from odoo import fields, models, _, api
from odoo.exceptions import UserError
from . import docusign


class ResCompany(models.Model):
    _inherit = "res.company"

    account_service_1 = fields.Selection([('audit', 'Audit'), ('accounting', 'Accounting')],
                                         required=True, default='audit')
    chartered_account_1_partner_id = fields.Many2one('res.partner',
                                                     domain="[('chartered_account_type', 'in', ['ec', 'ca'])]")
    account_service_2 = fields.Selection([('audit', 'Audit'), ('accounting', 'Accounting')],
                                         required=True, default='audit')
    chartered_account_2_partner_id = fields.Many2one('res.partner',
                                                     domain="[('chartered_account_type', 'in', ['ec', 'ca'])]")
    ds_service_name = fields.Char(string='Service name')
    ds_base_uri = fields.Char(string='Base URI')
    ds_email = fields.Char(string='Email')
    ds_password = fields.Char(string='Password')
    ds_integration_key = fields.Char(string='Integration key')
    ds_secret_key = fields.Char(string='Secret key')
    ds_sandbox = fields.Boolean(default=True, string='Test mode')

    @api.multi
    def check_docusign_connection(self):
        response_type = 'code'
        scope = 'signature'
        client_id = self.ds_integration_key
        redirect_uri = self.env['ir.config_parameter'].sudo().get_param('report.url') or \
                       self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirect_uri += '/docusign'

        try:
            client_action = {
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': docusign.REQUEST_URL[self.ds_sandbox] + 'docusign.com/oauth/auth' + '?response_type=' + response_type + '&scope=' + scope + '&client_id=' + client_id + '&redirect_uri=' + redirect_uri,
            }

            return client_action
        except Exception as e:
            raise UserError(
                _("Method doesn't work. Wrong credentials?\n%s" % (e))
            )

