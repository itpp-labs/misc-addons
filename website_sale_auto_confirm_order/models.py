from openerp import api, models, fields, SUPERUSER_ID

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def form_feedback(self, cr, uid, data, acquirer_name, context=None):
        res = super(PaymentTransaction, self).form_feedback(cr, uid, data, acquirer_name, context=context)

        tx = None
        # fetch the tx, check its state, confirm the potential SO
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(cr, uid, data, context=context)
        if tx:
            self.pool['sale.order'].action_button_confirm(cr, SUPERUSER_ID, [tx.sale_order_id.id], context=context)

        return True
