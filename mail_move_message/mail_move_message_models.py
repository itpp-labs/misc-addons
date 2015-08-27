from openerp import api, models, fields, SUPERUSER_ID
from openerp.tools.translate import _

class wizard(models.TransientModel):
    _name = 'mail_move_message.wizard'

    message_id = fields.Many2one('mail.message', string='Message')
    message_body = fields.Html(related='message_id.body', string='Message to move', readonly=True)
    message_moved_by_message_id = fields.Many2one('mail.message', related='message_id.moved_by_message_id', string='Moved with', readonly=True)
    message_moved_by_user_id = fields.Many2one('res.users', related='message_id.moved_by_user_id', string='Moved by', readonly=True)
    message_is_moved = fields.Boolean(string='Is Moved', related='message_id.is_moved', readonly=True)
    parent_id = fields.Many2one('mail.message', string='Search by name')
    model_id = fields.Many2one('ir.model', string='Model')
    res_id = fields.Many2one('ir.model', string='Record ID')
    record_url = fields.Char('Link to record', readonly=True)
    can_move = fields.Boolean('Can move', compute='get_can_move')
    move_back = fields.Boolean('Move to origin', help='Move  message and submessages to original place')
    model = fields.Char('Model', related='model_id.model')

    @api.depends('message_id')
    @api.one
    def get_can_move(self):
        # message was not moved before OR message is a top message of previous move
        self.can_move = not self.message_id.moved_by_message_id or self.message_id.moved_by_message_id.id == self.message_id.id

    @api.onchange('move_back')
    def on_change_move_back(self):
        if not self.move_back:
            return
        self.parent_id = self.message_id.moved_from_parent_id
        self.res_id = self.message_id.moved_from_res_id
        model = self.message_id.moved_from_model
        self.model_id = model and self.env['ir.model'].search([('model','=', model)])
    @api.onchange('parent_id', 'res_id', 'model_id')
    def update_move_back(self):
        model = self.message_id.moved_from_model
        model_id = model and self.env['ir.model'].search([('model','=', model)])
        self.move_back = self.parent_id == self.message_id.moved_from_parent_id \
                         and self.res_id == self.message_id.moved_from_res_id \
                         and (self.model_id == model_id or (not self.model_id and not model_id))

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
    def open_moved_by_message_id(self):
        message_id = None
        for r in self:
            message_id = r.message_moved_by_message_id.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail_move_message.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'context': {'default_message_id': message_id},
        }
    @api.multi
    def move(self):
        for r in self:
            r.check_access()
            if r.parent_id:
                if not (r.parent_id.model == r.model_id.model and
                        r.parent_id.res_id == r.res_id):
                    r.parent_id = None
            r.message_id.move(r.parent_id.id, r.res_id, r.model_id.model, r.move_back)

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

    @api.model
    def fields_get(self, fields=None, write_access=True, attributes=None):
        config_parameters = self.env['ir.config_parameter']
        res =  super(wizard, self).fields_get(fields, write_access=write_access, attributes=attributes)
        if 'model_id' in res:
            model_names = config_parameters.get_param('mail_relocation_models')
            if model_names:
                model_names = model_names.split(',')
                res['model_id']['domain'] = [('model', 'in', model_names)]
        return res

class mail_message(models.Model):
    _inherit = 'mail.message'

    is_moved = fields.Boolean('Is moved')
    moved_from_res_id = fields.Integer('Related Document ID (Original)')
    moved_from_model = fields.Char('Related Document Model (Original)')
    moved_from_parent_id = fields.Many2one('mail.message', 'Parent Message (Original)', ondelete='set null')
    moved_by_message_id = fields.Many2one('mail.message', 'Moved by message', ondelete='set null', help='Top message, that initate moving this message')
    moved_by_user_id = fields.Many2one('res.users', 'Moved by user', ondelete='set null')
    all_child_ids = fields.One2many('mail.message', string='All childs', compute='_get_all_childs', help='all childs, including subchilds')

    @api.one
    def _get_all_childs(self, include_myself=True):
        ids = []
        if include_myself:
            ids.append(self.id)
        while True:
            new_ids = self.search([('parent_id', 'in', ids), ('id', 'not in', ids)]).ids
            if new_ids:
                ids = ids + new_ids
                continue
            break
        moved_childs = self.search([('moved_by_message_id', '=', self.id)]).ids
        self.all_child_ids = ids + moved_childs

    @api.one
    def move(self, parent_id, res_id, model, move_back):
        vals = {}
        if move_back:
            # clear variables if we move everything back
            vals['is_moved'] = False
            vals['moved_by_user_id'] = None
            vals['moved_by_message_id'] = None

            vals['moved_from_res_id'] = None
            vals['moved_from_model'] = None
            vals['moved_from_parent_id'] = None
        else:
            vals['parent_id'] = parent_id
            vals['res_id'] = res_id
            vals['model'] = model

            vals['is_moved'] = True
            vals['moved_by_user_id'] = self.env.user.id
            vals['moved_by_message_id'] = self.id

        for r in self.all_child_ids:
            r_vals = vals.copy()
            if not r.is_moved:
                # moved_from_* variables contain not last, but original
                # reference
                r_vals['moved_from_parent_id'] = r.parent_id.id
                r_vals['moved_from_res_id'] = r.res_id
                r_vals['moved_from_model'] = r.model
            elif move_back:
                r_vals['parent_id'] = r.moved_from_parent_id.id
                r_vals['res_id'] = r.moved_from_res_id
                r_vals['model'] = r.moved_from_model
            print 'update message', r, r_vals
            r.sudo().write(r_vals)

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
            name = record['record_name'] or ''
            extended_name = '   [%s] ID %s' % (record.get('model', 'UNDEF'), record.get('res_id', 'UNDEF'))
            res.append((record['id'], name + extended_name))
        return res

    def _message_read_dict(self, cr, uid, message, parent_id=False, context=None):
        res = super(mail_message, self)._message_read_dict(cr, uid, message, parent_id, context)
        res['is_moved'] = message.is_moved
        return res


class mail_move_message_configuration(models.TransientModel):
    _name = 'mail_move_message.config.settings'
    _inherit = 'res.config.settings'

    model_ids = fields.Many2many(comodel_name='ir.model', string='Models')

    @api.model
    def get_default_model_ids(self, fields):
        config_parameters = self.env['ir.config_parameter']
        model_obj = self.env['ir.model']
        model_names = config_parameters.get_param('mail_relocation_models')
        if not model_names:
            return {}
        model_names = model_names.split(',')
        model_ids = model_obj.search([('model', 'in', model_names)])
        return {'model_ids': [m.id for m in model_ids]}

    @api.multi
    def set_model_ids(self):
        config_parameters = self.env['ir.config_parameter']
        model_names = ''
        for record in self:
            model_names = ','.join([m.model for m in record.model_ids])
            config_parameters.set_param('mail_relocation_models', model_names)
