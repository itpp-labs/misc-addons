# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import SUPERUSER_ID

class crm_lead(osv.Model):
    _inherit = "crm.lead"
    def create(self, cr, uid, vals, context=None):

       channel_id = None
       try:
           channel_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'crm', 'crm_case_channel_website')[1]
       except ValueError:
           pass
       if channel_id is not None and \
              vals.has_key('channel_id') and \
              channel_id == vals['channel_id'] and \
              not vals.has_key('section_id'):
         section_ids = self.pool.get("crm.case.section").search(
             cr, SUPERUSER_ID, [("code", "=", "Website")], context=context)
         if section_ids:
             vals['section_id'] = section_ids[0]

       return super(crm_lead, self).create(cr, uid, vals, context=context)
