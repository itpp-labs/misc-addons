from odoo import models, fields, api
from datetime import datetime,timedelta

class Service_Scheduler(models.Model):
	_inherit = 'sale.order'

	order_count = fields.Integer(string="Order Count")

	# def service_scheduler(self): 
	# 	sale_orders = self.search([])
	# 	for sale_order in sale_orders:
	# 		if sale_order.confirmation_date:
	# 			service_datetime = datetime.strptime(sale_order.confirmation_date,'%Y-%m-%d %H:%M:%S') + timedelta(days=90)
	# 			service_duration = service_datetime

	# 			if service_duration >= datetime.today():
	# 				print('-----------------------------')
	# 				print('heloo!!!')
	# 				print('-----------------------------')
	# 				email_template_obj = self.env['mail.template']
	# 				template_ids = self.env['ir.model.data'].get_object_reference(
	# 				'sale', 'send_service_remainder')[1]
	# 				email_template = email_template_obj.search([('id', '=', template_ids)])
	# 				if email_template:
	# 					vals = email_template.generate_email(self.id)
	# 					vals['email_to'] = self.major_unit_id.partner_id.email
	# 					mail_mail_obj = self.env['mail.mail']
	# 					msg_id = mail_mail_obj.create(vals)
	# 					if msg_id:
	# 					    msg_id.send([msg_id])