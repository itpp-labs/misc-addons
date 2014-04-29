# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class project_task(osv.Model):
    _inherit = "project.task"
    def _x_out_amount_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if not (task.x_currency_in_id and task.x_currency_out_id):
                return {}
            
            cur_in = task.x_currency_in_id.rate
            cur_out = task.x_currency_out_id.rate
            
            x_out_amount = task.x_in_amount / cur_in * cur_out
            res[task.id] = x_out_amount
        return res


    def onchange_currency(self, cr, uid, ids, x_currency_in_id, x_currency_out_id, x_in_amount, x_out_amount):
        currency_obj = self.pool.get('res.currency')
        
        if not (x_currency_in_id and x_currency_out_id):
            return {}
        
        cur_in = currency_obj.browse(cr, uid, x_currency_in_id)
        cur_out = currency_obj.browse(cr, uid, x_currency_out_id)

        update_in = False
        if update_in:
            val = {'x_in_amount':  x_out_amount / cur_out.rate * cur_in.rate}
        else:
            val = {'x_out_amount': x_in_amount / cur_in.rate * cur_out.rate}
        return {'value':val}
        
    _columns = {
        'x_currency_in_id': fields.many2one('res.currency', 'Money IN', required=True),  #	Money IN	many2one			Поиск не производится	Пользовательское поле
        'x_currency_out_id': fields.many2one('res.currency', 'Money OUT', required=True), #	Money OUT	many2one			Поиск не производится	Пользовательское поле
        'x_in_amount':fields.float('Amount IN'), #	Amount	float			Поиск не производится	Пользовательское поле
        'x_out_amount':fields.function(_x_out_amount_get, string='Amount Out',
                                       store = {
                                           'project.task':(lambda self, cr, uid, ids, c={}: ids, ['x_currency_in_id', 'x_currency_out_id', 'x_in_amount'], 10)
                                       })#	Payment amount	float			Поиск не производится	Пользовательское поле


        #'x__task_cur_1'#	Test	many2many			Поиск не производится	Пользовательское поле
        #'x_currency_id_1_1'#	test	many2one			Поиск не производится	Пользовательское поле
        #'x_pay_details_benef'#	Beneficiary's Name	char			Поиск не производится	Пользовательское поле
        #'x_pay_details_benef_account'#	Account number	char			Поиск не производится	Пользовательское поле
        #'x_pay_details_benef_adress'#	Adress	char			Поиск не производится	Пользовательское поле
        #'x_pay_details_benef_city'#	City	char			Поиск не производится	Пользовательское поле
        #'x_x_pay_details_benef_swift'#	SWIFT	char			Поиск не производится	Пользовательское поле
    }

