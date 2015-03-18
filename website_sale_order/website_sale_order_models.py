from openerp import api,models,fields,SUPERUSER_ID
from openerp.osv import fields as old_fields

class res_partner(models.Model):
    _inherit = 'res.partner'
    _columns = {
        'name': old_fields.char('Name', required=True, select=True, track_visibility='onchange'),
        'phone': old_fields.char('Phone', track_visibility='onchange'),
    }
