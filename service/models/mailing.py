from odoo import models, fields, api
import datetime


class email_trigger(models.Model):

    _name = 'service.mailing'

    def create_annual_send_mail(self, customer):
        email_template_obj = self.env['mail.template']
        template_ids = self.env['ir.model.data'].get_object_reference(
            'service', 'email_template_annual_form')[1]
        email = customer['email']
        name = customer['name']
        email_template = email_template_obj.search([('id', '=', template_ids)])
        if email_template:
            values = email_template.generate_email(customer['id'])
            values['email_to'] = email
            values['record_name'] = name
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                msg_id.send(customer['id'])
        return True

    def annual_email_trigger_action(self):
        customer_data = self.env[
            'major_unit.major_unit'].search([('id', '>', "0")])
        for val in customer_data:
            if val.purchase_date:
                today = datetime.datetime.today().strftime('%Y-%m-%d')
                date_format = "%Y-%m-%d"
                a = datetime.datetime.strptime(val.purchase_date, date_format)
                b = datetime.datetime.strptime(today, date_format)
                delta = b-a
                delta = delta.days
                if delta == -365:
                	if val.partner_id:
	                    val = {
	                    	'id':val.partner_id.id,
	                        'name': val.partner_id.name,
	                        'email': val.partner_id.email,
	                    }
	                    self.create_annual_send_mail(val)
        return True


    def create_600m_send_mail(self, customer):
        email_template_obj = self.env['mail.template']
        template_ids = self.env['ir.model.data'].get_object_reference(
            'service', 'email_template_600_form')[1]
        email = customer['email']
        name = customer['name']
        email_template = email_template_obj.search([('id', '=', template_ids)])
        if email_template:
            values = email_template.generate_email(customer['id'])
            values['email_to'] = email
            values['record_name'] = name
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                msg_id.send(customer['id'])
        return True

    def email_trigger_600m_action(self):
        customer_data = self.env[
            'major_unit.major_unit'].search([('id', '>', "0")])
        for val in customer_data:
            if val.purchase_date:
                today = datetime.datetime.today().strftime('%Y-%m-%d')
                date_format = "%Y-%m-%d"
                a = datetime.datetime.strptime(val.purchase_date, date_format)
                b = datetime.datetime.strptime(today, date_format)
                delta = b-a
                delta = delta.days
                if delta == -30:
                	if val.partner_id:
	                    val = {
	                    	'id':val.partner_id.id,
	                        'name': val.partner_id.name,
	                        'email': val.partner_id.email,
	                    }
	                    self.create_600m_send_mail(val)
        return True