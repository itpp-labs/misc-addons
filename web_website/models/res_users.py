# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):

    _inherit = 'res.users'

    backend_website_id = fields.Many2one(
        'website',
        'Current Backend Website',
    )
    backend_website_ids = fields.Many2many(
        'website',
        'Allowed Backend Websites',
        help='Computed automatically based on Current Company field',
        compute='_compute_backend_website_ids',
    )
    backend_websites_count = fields.Integer(
        compute='_compute_backend_website_ids',
    )

    def _compute_backend_website_ids(self):
        for r in self:
            websites = self.env['website'].search([
                ('company_id', 'in', [False] + [r.company_id.id])
            ])
            r.backend_website_ids = websites
            r.backend_websites_count = len(websites)

    def write(self, vals):
        if 'company_id' in vals and 'backend_website_id' not in vals:
            vals['backend_website_id'] = False
        return super(ResUsers, self).write(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            if self.backend_website_id.company_id != self.company_id:
                self.backend_website_id = None

        self._compute_backend_website_ids()

        return {'domain': {
            'backend_website_id': [
                ('company_id', 'in', self.company_id.ids or [])
            ]
        }}

    @api.constrains('company_id', 'backend_website_id')
    def _check_backend_website_in_current_company(self):
        for record in self:
            if record.backend_website_id \
                    and record.company_id \
                    and record.backend_website_id.company_id \
                    and record.backend_website_id.company_id != record.company_id:
                raise ValidationError(_("Current website doesn't belong to Current Company"))

