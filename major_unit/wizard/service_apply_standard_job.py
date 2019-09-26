from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ServiceApplyStandardJobs(models.TransientModel):
    _name = "service.apply.standard.job"
    _description = "Apply Standard Jobs"

    repair_order_id = fields.Many2one('service.repair_order', 'Repair Order', required=True)
    standard_job_ids = fields.Many2many('service.standard_job', string='Standard Jobs', required=True)

    @api.model
    def default_get(self, fields):
        res = super(ServiceApplyStandardJobs, self).default_get(fields)
        if (not res.get('repair_order_id') and self.env.context.get('active_id') and
                self.env.context.get('active_model') == 'service.repair_order'):
            res['repair_order_id'] = self.env['service.repair_order'].browse(self.env.context['active_id']).id
        return res

    @api.onchange('repair_order_id')
    def _onchange_repair_order(self):
        major_unit = self.env['major_unit.major_unit'].browse(self.env.context.get('major_unit_id'))
        fitments = self.env['product.fitment'].get_fitment_by_make_model_year(self.get_make_model_year(major_unit))
        return {'domain': {'standard_job_ids': [('fitment_ids', 'in', fitments.ids), ('recall', '=', False)]}}

    @api.model
    def get_make_model_year(self, major_unit):
        attribute_value_ids = major_unit.mapped('attribute_value_ids')
        make = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_make)).id
        model = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_model)).id
        year = attribute_value_ids.filtered(
            lambda r: r.attribute_id == r.env.ref(r.env['product.fitment']._product_attribute_year)).id
        return make, model, year

    @api.multi
    def apply_standard_job(self):
        for wizard in self:
            for standard_job in wizard.standard_job_ids:
                for product_line in standard_job.product_ids:
                    self.env['service.repair_order.product'].create({
                        'repair_order_id': wizard.repair_order_id.id,
                        'product_id': product_line.product_id.id,
                        'standard_job_id': standard_job.id,
                        'quantity': product_line.quantity,
                    })
        return {'type': 'ir.actions.act_window_close'}
