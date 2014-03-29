from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    def _get_advance_payment_method(self, cr, uid, context=None):
        res = None
        try:
            res = context['advance_payment_method']
        except:
            pass
        return res or 'all'

    _defaults = {
        'advance_payment_method': _get_advance_payment_method,
        }
