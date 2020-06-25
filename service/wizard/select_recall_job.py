from odoo import api, models, fields, tools, _


class ServiceSelectRecallJob(models.TransientModel):
    _name = "service.select.recall.job"
    _description = "Select Recall Job"

    repair_order_id = fields.Many2one('service.repair_order', 'Repair Order', required=True)
    standard_job_id = fields.Many2one('service.standard_job', string='Standard Jobs', required=True)

    @api.model
    def default_get(self, fields):
        res = super(ServiceSelectRecallJob, self).default_get(fields)
        if (not res.get('repair_order_id') and self.env.context.get('active_id') and
                self.env.context.get('active_model') == 'service.repair_order'):
            res['repair_order_id'] = self.env['service.repair_order'].browse(self.env.context['active_id']).id
        return res

    @api.multi
    def select_recall_job(self):
        for w in self:
            w.repair_order_id.claim_id = w.standard_job_id.claim_id
            w.repair_order_id.manufacturer = w.standard_job_id.manufacturer
            w.repair_order_id.defect_group = w.standard_job_id.defect_group
            w.repair_order_id.defect_code = w.standard_job_id.defect_code
            w.repair_order_id.defect_type = w.standard_job_id.defect_type
            w.repair_order_id.cause = w.standard_job_id.cause
        return {'type': 'ir.actions.act_window_close'}