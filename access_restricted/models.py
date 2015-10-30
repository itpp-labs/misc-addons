from openerp import models, api, exceptions, SUPERUSER_ID

IR_CONFIG_NAME = 'access_restricted.fields_view_get_uid'


class ResUsers(models.Model):
    _inherit = 'res.users'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if view_type == 'form':
            last_uid = self.pool['ir.config_parameter'].get_param(cr, uid, IR_CONFIG_NAME, context=context)
            if int(last_uid) != uid:
                self.pool['ir.config_parameter'].set_param(cr, uid, IR_CONFIG_NAME, uid, context=context)
                self.pool['res.groups'].update_user_groups_view(cr, uid, context=context)

        return super(ResUsers, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)

    def fields_get(self, cr, uid, allfields=None, context=None, write_access=True, attributes=None):
        # inherited as uid here is always SUPERUSER_ID
        uid = self.pool['ir.config_parameter'].get_param(cr, uid, IR_CONFIG_NAME, context=context)
        uid = int(uid)
        return super(ResUsers, self).fields_get(cr, uid, allfields=None, context=None, write_access=True, attributes=None)

class IRRule(models.Model):
    _inherit = 'ir.rule'

    @api.multi
    def check_restricted(self):
        if self.env.user.id == SUPERUSER_ID:
            return
        g = self.env.ref('access_restricted.res_groups_restricted')
        for r in self:
            if r.id == g.id:
                raise exceptions.Warning("You don't have access for this operation")

    @api.multi
    def write(self, vals):
        self.check_restricted()
        return super(IRRule, self).write(vals)

    @api.multi
    def unlink(self):
        self.check_restricted()
        return super(IRRule, self).unlink()
