from openerp import api, models, fields, SUPERUSER_ID
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class mrp_repair(models.Model):
    _inherit = 'mrp.repair'

    customer_po = fields.Char('Customer PO')
    close_date = fields.Datetime('Closed on')
    open_time = fields.Integer(string='Open time (days)', compute='_get_open_time')

    @api.one
    #@api.depends('state')
    def _get_open_time(self):
        res = None
        start_date = self.create_date or fields.Datetime.now()
        end_date = fields.Datetime.now()
        if self.state == 'done':
            if not self.close_date:
                self.write({'close_date': self.write_date})
            end_date = self.close_date
        d = datetime.strptime(end_date, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        res = d.days + 1
        self.open_time = res

    @api.model
    def update_open_time(self):
        self.search([('state', 'not in', ['done', 'cancel'])])._get_open_time()

    @api.v7
    def action_repair_done(self, cr, uid, ids, context=None):
        print ' *** action_repair_done'
        res = super(mrp_repair, self).action_repair_done(cr, uid, ids, context)
        self.write(cr, uid, ids, {'close_date': fields.Datetime.now()}, context=context)
        return res
