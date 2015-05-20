# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
import re


class res_partner(models.Model):
    _inherit = 'res.partner'
    vk = fields.Char(string="VK", size=64)

    @api.one
    def write(self, vals):
        vals = self._check_vk_field(vals)
        return super(res_partner, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self._check_vk_field(vals)
        return super(res_partner, self).create(vals)

    def _check_vk_field(self, vals):
        if vals.get('vk'):
            vk = vals['vk'].strip()
            regex_1 = r'^\w+$'
            if re.findall(regex_1, vk):
                vk = "https://vk.com/"+vk
            else:
                vk = re.sub("^(http|https)://(vkontakte|vk).(ru|com)",
                            "https://vk.com", vk)
            vals['vk'] = vk
        return vals

    @api.one
    @api.constrains('vk')
    def _check_something(self):
        regex = r'^https://vk.com/\w+$'
        if not re.findall(regex, self.vk):
            raise ValidationError("VK address %s is not valid.\n The address \
                must be in the format: https://vk.com/id" % self.vk)
