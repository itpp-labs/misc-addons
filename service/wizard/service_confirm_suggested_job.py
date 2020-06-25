from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import datetime


class ServiceConfirmSuggestedJobs(models.TransientModel):
    _name = "confirm.suggested.job"
    _description = "Confirm Suggested Jobs"

    repair_order_id = fields.Many2one('service.repair_order',
                                      'Repair Order',
                                      required=False)
    standard_job_line_ids = fields.One2many('confirm.suggested.job.line',
                                            'parent',
                                            string='Standard Job Lines',
                                            required=True)
    inspect_id = fields.Many2one(
        'service.inspection', 'Inspect Order', required=False, ondelete='cascade')
    confirm_date = fields.Datetime('Confirm Date')
    reconfirm_date = fields.Datetime('Re-confirm Date')

    @api.model
    def default_get(self, fields):
        res = super(ServiceConfirmSuggestedJobs, self).default_get(fields)
        if not res.get('repair_order_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.repair_order':
            repair_order_id = self.env['service.repair_order'].browse(
                self.env.context['active_id'])
        elif not res.get('inspect_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'service.inspection':
            inspect_id = self.env['service.inspection'].browse(
                self.env.context['active_id'])
            res['inspect_id'] = inspect_id.id
            repair_order_id = inspect_id.repair_order_id
        res['repair_order_id'] = repair_order_id.id
        suggested_jobs = []
        for suggested_job in repair_order_id.suggested_job_ids:
            if suggested_job.state not in ['approved', 'rejected']:
                suggested_jobs.append([0, 0, {'standard_job_id': suggested_job.standard_job_id.id, 'quantity':
                                              suggested_job.quantity, 'product_id': suggested_job.product_id.id, 'confirm': False}])
        res['standard_job_line_ids'] = suggested_jobs
        return res

    @api.multi
    def confirm_suggested_job(self):
        for wizard in self:
            standard_jobs = wizard.repair_order_id.standard_job_ids.ids
            for standard_job_line in wizard.standard_job_line_ids:
                if standard_job_line.confirm:

                    standard_job_product_obj = self.env[
                        'service.repair_order.product']
                    standard_job_product_search = standard_job_product_obj.search([
                        ('repair_order_id', '=', wizard.repair_order_id.id),
                        ('standard_job_id', '=',
                         standard_job_line.standard_job_id.id),
                        ('product_id', '=', standard_job_line.product_id.id)])
                    if not standard_job_product_search:
                        standard_job_product_obj.create({
                            'repair_order_id': wizard.repair_order_id.id,
                            'product_id': standard_job_line.product_id.id,
                            'standard_job_id': standard_job_line.standard_job_id.id,
                            'quantity': standard_job_line.quantity,
                        })
                        self.create_new_workorder(
                            standard_job_line.standard_job_id)
                        self.repair_order_id.create_sale_order()

                    suggested_job_obj = self.env[
                        'service.suggested.standard_job']
                    suggested_job_search = suggested_job_obj.search([
                        ('repair_order_id', '=', wizard.repair_order_id.id),
                        ('standard_job_id', '=',
                         standard_job_line.standard_job_id.id),
                        ('product_id', '=', standard_job_line.product_id.id)])
                    suggested_job_search.write({'state': 'approved'})
                    if standard_job_line.standard_job_id.id not in standard_jobs:
                        standard_jobs.append(
                            standard_job_line.standard_job_id.id)
                        wizard.repair_order_id.write(
                            {'standard_job_ids': [[6, 0, standard_jobs]]})
                        if self.repair_order_id.confirm_date:
                            self.repair_order_id.write({'state': 'APPROVE',
                                                        'reconfirm_date': datetime.datetime.now()})
                        else:
                            self.repair_order_id.write({'state': 'APPROVE',
                                                        'confirm_date': datetime.datetime.now()})

        self.repair_order_id.action_confirm()

        return {'type': 'ir.actions.act_window_close'}

    def _prepare_workorders(self, job):
        res = {'standard_job_id': job.id,
               'name': job.name,
               'repair_order_id': self.repair_order_id.id,
               'vehicle_id': self.repair_order_id.major_unit_id.id,
               'partner_id': self.repair_order_id.partner_id.id,
               }
        return res

    @api.multi
    def create_new_workorder(self, standard_job_ids):
        for job in standard_job_ids:
            if self.repair_order_id.workorder_exist(job):
                continue
            my_workorder_details = self.env['drm.workorders'].create(
                self._prepare_workorders(job))


class ServiceSuggestedJobLines(models.TransientModel):
    _name = "confirm.suggested.job.line"
    _description = "Confirm Suggested Jobs Lines"

    parent = fields.Many2one('confirm.suggested.job', string="Parent")
    product_id = fields.Many2one('product.product',
                                 'Parts/Labor',
                                 required=True,
                                 domain=[('details_model', 'in', ['product.template.details', 'labor'])])

    standard_job_id = fields.Many2one('service.standard_job',
                                      string='Standard Jobs',
                                      required=True,
                                      domain="[('active_job', '=', True),('publish_job', '=', True)]")
    confirm = fields.Boolean(string="Confirm", readonly=False)
    quantity = fields.Float('Quantity',
                            digits=dp.get_precision('Product Unit of Measure'),
                            default=1)
