from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class StandardJob(models.Model):
    _inherit = 'mail.thread'
    _inherit = 'service.standard_job'
    _description = 'Standard Job'

    active_job = fields.Boolean(string='Active')
    publish_job = fields.Boolean(string='Publish')
    repair_type = fields.Selection([('required_maintenance', 'Required Maintenance'),
                                    ('other', 'Other')],
                                   String='Priority',
                                   required=True,
                                   default='required_maintenance')

    document = fields.Binary('Document')
    standard_job_image = fields.Binary(string="Job Image")
    bundle_amount_total = fields.Float(string='Total',
                                       store=False,
                                       readonly=True,
                                       compute='_compute_amount_all',

                                       )

    standard_job_type = fields.Selection([('part', 'Part'), ('labor', 'Labor'),
                                          ('other', 'Other')],
                                         String='Type of Standard Job',
                                         required=True,
                                         readonly=True,
                                         default='other')

    job_description = fields.Text(string="Job Description")
    hours = fields.Char(string ="Hours")
    part_number=fields.Char(string ="Part Number", required=True)
    loc=fields.Many2one('product.attribute', 'Attribute',default=lambda self: self.env['product.attribute'].search([('name','=','Location')]))
    store_location = fields.Many2many('product.attribute.value', string='Location', ondelete='restrict',required=True )
    priority = fields.Selection([
        ('0', 'Low'), ('1', 'Medium'),
        ('2', 'High'), ('3', 'Highest')],
        'Job Level', required=True, default='1')

    @api.depends('product_ids.price')
    def _compute_amount_all(self):
        for order in self:
            amount_untaxed = 0.0
            for line in order.product_ids:
                amount_untaxed += line.price
            order.update({
                'bundle_amount_total': amount_untaxed
            })

    @api.multi
    def toggle_active(self):
        if self.active_job:
            self.write({'active_job': False})
        else:
            self.write({'active_job': True})

    # @api.multi
    # def _get_location(self):

    #     location_id=self.env['product.attribute'].search([('name','=','Location')])
    #     self.loc=location_id.id
    #     return self.loc

    @api.multi
    def toggle_publish(self):
        if self.publish_job:
            self.write({'publish_job': False})
        else:
            self.write({'publish_job': True})
