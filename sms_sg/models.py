# -*- coding: utf-8 -*-

from openerp import models, fields, api
import requests


class SendAndLog(models.Model):
    _name = 'sms_sg.sendandlog'

    msg = fields.Char()
    phone = fields.Char()
    response_content = fields.Char()

    @api.model
    def send_sms(self, phone, msg):
        user = self.env['ir.config_parameter'].search([('key', '=', 'smssg_user')], limit=1).value
        pwd = self.env['ir.config_parameter'].search([('key', '=', 'smssg_pwd')], limit=1).value
        payload = {'msg': msg, 'to': phone,
                   'pwd': pwd,
                   'user': user,
                   'option': 'send'}
        r = requests.get('http://www.sms.sg/http/sendmsg', params=payload)
        self.create({'msg': msg, 'phone': phone, 'response_content': r.content})
