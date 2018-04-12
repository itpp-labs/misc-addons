# -*- coding: utf-8 -*-
from odoo import models, api


class IrProperty(models.Model):
    _inherit = 'ir.property'

    @api.multi
    def write(self, vals):
        res = super(IrProperty, self).write(vals)
        self._update_config_parameter_value()
        return res

    @api.multi
    def _update_config_parameter_value(self):
        """Check for default value in ir.config_parameter
        and copy value to "value" column"""
        field = self.env.ref('base.field_ir_config_parameter_value')
        for r in self:
            if r.fields_id != field:
                # It's not for ir.config_parameter
                continue
            if r.company_id:
                # it's not default value
                continue
            if not r.res_id:
                # Paramater is not specified
                continue
            # Default value is updated. Set new value in column "value"
            model, res_id = r.res_id.split(',')
            value = r.get_by_record()
            param = self.env['ir.config_parameter'].browse(int(res_id))
            param._update_db_value(value)
