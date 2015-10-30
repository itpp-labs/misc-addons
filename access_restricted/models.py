from openerp import models, api, exceptions, SUPERUSER_ID

IR_CONFIG_NAME = 'access_restricted.fields_view_get_uid'


class ResUsers(models.Model):
    _inherit = 'res.users'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if view_type == 'form':
            last_uid = self.pool['ir.config_parameter'].get_param(cr, uid, IR_CONFIG_NAME, context=context)
            if int(last_uid) != uid:
                ctx = (context or {}).copy()
                ctx['access_restricted'] = 1
                self.pool['res.groups'].update_user_groups_view(cr, uid, context=ctx)

        return super(ResUsers, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)

    def fields_get(self, cr, uid, allfields=None, context=None, write_access=True, attributes=None):
        # uid is SUPERUSER_ID, so we need to change it
        uid = self.pool['ir.config_parameter'].get_param(cr, uid, IR_CONFIG_NAME, context=context)
        uid = int(uid)
        ctx = (context or {}).copy()
        ctx['access_restricted'] = 1
        return super(ResUsers, self).fields_get(cr, uid, allfields=allfields, context=ctx, write_access=write_access, attributes=attributes)


class ResGroups(models.Model):
    _inherit = 'res.groups'

    def update_user_groups_view(self, cr, uid, context=None):
        self.pool['ir.config_parameter'].set_param(cr, uid, IR_CONFIG_NAME, uid, context=context)
        ctx = (context or {}).copy()
        ctx['access_restricted'] = 1
        return super(ResGroups, self).update_user_groups_view(cr, uid, context=ctx)

    def get_application_groups(self, cr, uid, domain=None, context=None):
        if domain is None:
            domain = []
        domain.append(('share', '=', False))
        if uid != SUPERUSER_ID and (context or {}).get('access_restricted'):
            model_data_obj = self.pool.get('ir.model.data')
            _model, group_no_one_id = model_data_obj.get_object_reference(cr, uid, 'base', 'group_no_one')
            domain = domain + ['|', ('users', 'in', [uid]), ('id', '=', group_no_one_id)]
        return self.search(cr, uid, domain, context=context)
