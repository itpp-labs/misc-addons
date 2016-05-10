from openerp import api, models, fields


class account_invoice(models.Model):

    _inherit = "account.invoice"

    @api.multi
    def _get_analytic_lines(self):
        res = super(account_invoice, self)._get_analytic_lines()
        for move in res:
            start_date = move.get('start_date')
            end_date = move.get('end_date')
            for add_line in move.get('analytic_lines', []):
                # add_line = (0, 0, {...})
                line = add_line[2]
                line['start_date'] = start_date
                line['end_date'] = end_date
        return res

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        res['start_date'] = line.get('start_date')
        res['end_date'] = line.get('end_date')
        return res

class account_move_line(models.Model):

    _inherit = "account.move.line"

    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')

    def _prepare_analytic_line(self, cr, uid, obj_line, context=None):
        res = super(account_move_line, self)._prepare_analytic_line(cr, uid, obj_line, context=context)
        res['start_date'] = obj_line.start_date
        res['end_date'] = obj_line.end_date
        return res

class account_invoice_line(models.Model):

    _inherit = "account.invoice.line"

    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')

    @api.model
    def move_line_get_item(self, line):
        res = super(account_invoice_line, self).move_line_get_item(line)
        res['start_date'] = line.start_date
        res['end_date'] = line.end_date
        return res

class account_analytic_line(models.Model):

    _inherit = "account.analytic.line"

    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
