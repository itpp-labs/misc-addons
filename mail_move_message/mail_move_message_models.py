from openerp import api, models, fields, SUPERUSER_ID
from openerp.tools.translate import _

class wizard(models.TransientModel):
    _name = 'mail_move_message.wizard'

    message_id = fields.Many2one('mail.message', string='Message')
    message_body = fields.Html(related='message_id.body', string='Message to move', readonly=True)
    parent_id = fields.Many2one('mail.message', string='Search by name')
    model_id = fields.Many2one('ir.model', string='Record type')
    res_id = fields.Integer('Record ID')
    record_url = fields.Char('Link to record', readonly=True)

    @api.onchange('parent_id')
    def on_change_parent_id(self):
        if self.parent_id and self.parent_id.model:
            self.model_id = self.env['ir.model'].search([('model', '=', self.parent_id.model)])[0]
            self.res_id = self.parent_id.res_id
        else:
            self.model_id = None
            self.res_id = None

    @api.onchange('model_id', 'res_id')
    def on_change_res(self):
        if not ( self.model_id and self.res_id ):
            self.record_url = ''
            return

        self.record_url = '/web#id=%s&model=%s' % (self.res_id, self.model_id.model)

    @api.one
    def check_access(self):
        cr = self._cr
        uid = self.env.user.id
        operation = 'write'
        context = self._context

        if not ( self.model_id and self.res_id ):
            return True
        model_obj = self.pool[self.model_id.model]
        mids = model_obj.exists(cr, uid, [self.res_id])
        if hasattr(model_obj, 'check_mail_message_access'):
            model_obj.check_mail_message_access(cr, uid, mids, operation, context=context)
        else:
            self.pool['mail.thread'].check_mail_message_access(cr, uid, mids, operation, model_obj=model_obj, context=context)

    @api.multi
    def move(self):
        for r in self:
            r.check_access()
            if r.parent_id:
                if not (r.parent_id.model == r.model_id.model and
                        r.parent_id.res_id == r.res_id):
                    r.parent_id = None
            ids = [r.message_id.id]
            while True:
                new_ids = self.env['mail.message'].search([('parent_id', 'in', ids), ('id', 'not in', ids)]).ids
                if new_ids:
                    ids = ids + new_ids
                    continue
                break
            r.message_id.sudo().write({'parent_id': r.parent_id.id})
            self.env['mail.message'].sudo().search([('id', 'in', ids)]).write({'res_id': r.res_id, 'model': r.model_id.model})
            
        if not ( r.model_id and r.res_id ):
            obj = self.pool.get('ir.model.data').get_object_reference(self._cr, SUPERUSER_ID, 'mail', 'mail_archivesfeeds')[1]
            return {
                'type' : 'ir.actions.client',
                'name' : 'Archive',
                'tag' : 'reload',
                'params' : {'menu_id': obj},
            }
        return {
            'name': _('Record'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': r.model_id.model,
            'res_id': r.res_id,
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
        }

class mail_message(models.Model):
    _inherit = 'mail.message'

    def name_get(self, cr, uid, ids, context=None):
        if not (context or {}).get('extended_name'):
            return super(mail_message, self).name_get(cr, uid, ids, context=context)
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['record_name','model', 'res_id'], context=context)
        res = []
        for record in reads:
            name = record['record_name']
            extended_name = '   [%s] ID %s' % (record.get('model', 'UNDEF'), record.get('res_id', 'UNDEF'))
            res.append((record['id'], name + extended_name))
        return res
