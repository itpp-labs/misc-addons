# -*- coding: utf-8 -*-
from openerp import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    _track = {
        'date_action': {
            'crm_next_action.mt_lead_next_action_date': lambda self, cr, uid, obj, ctx=None: True
        },
        'title_action': {
            'crm_next_action.mt_lead_next_action': lambda self, cr, uid, obj, ctx=None: True
        }
    }

    date_action = fields.Date('Next Action Date', select=True, track_visibility='onchange')
    title_action = fields.Char('Next Action', track_visibility='onchange')

