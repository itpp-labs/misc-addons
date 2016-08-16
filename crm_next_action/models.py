# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class CrmLead(osv.osv):
    _inherit = 'crm.lead'

    _track = {
        'date_action': {
            'crm_next_action.mt_lead_next_action_date': lambda self, cr, uid, obj, ctx=None: True
        },
        'title_action': {
            'crm_next_action.mt_lead_next_action': lambda self, cr, uid, obj, ctx=None: True
        }
    }
    _columns = {
        'date_action': fields.date('Next Action Date', select=True, track_visibility='onchange'),
        'title_action': fields.char('Next Action', track_visibility='onchange'),
    }
