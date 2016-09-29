# -*- coding: utf-8 -*-
from openerp import models, fields


class CrmPhonecall(models.Model):
    _inherit = 'crm.phonecall'

    _track = {
        'partner_id': {
            'crm_phonecall_notification.mt_phonecall_new': lambda self, cr, uid, obj, ctx=None: obj.partner_id
        }
    }

    name = fields.Char('Call Summary', required=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Contact', track_visibility='onchange')


    def _add_followers(self, cr, uid, vals, context):
        vals = vals or {}
        vals['message_follower_ids'] = vals.get('message_follower_ids') or []
        partner_ids = []
        if vals.get('partner_id'):
            # partner_ids.append(vals.get('partner_id'))
            r = self.pool['res.partner'].browse(cr, uid, vals.get('partner_id'), context=context)
            if r.user_id and r.user_id.partner_id:
                partner_ids.append(r.user_id.partner_id.id)

        if vals.get('user_id'):
            r = self.pool['res.users'].browse(cr, uid, vals.get('user_id'), context=context)
            partner_ids.append(r.partner_id.id)
        for partner_id in partner_ids:
            vals['message_follower_ids'].append((4, partner_id))
        return vals

    def create(self, cr, uid, vals, context=None):
        vals = self._add_followers(cr, uid, vals, context)

        ctx = context.copy()
        # fix bug:
        # ValueError: Wrong value for mail.mail.state: 'done'
        state = ctx.get('default_state')
        if state and not vals.get('state'):
            vals['state'] = state
            del ctx['default_state']

        return super(CrmPhonecall, self).create(cr, uid, vals, context=ctx)

    def write(self, cr, uid, ids, vals, context=None):
        vals = self._add_followers(cr, uid, vals, context)

        ctx = context.copy()
        try:
            del ctx['default_state']
        except:
            pass

        return super(CrmPhonecall, self).write(cr, uid, ids, vals, context=ctx)
