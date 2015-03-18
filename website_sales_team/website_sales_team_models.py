from openerp import api,models,fields,SUPERUSER_ID
from openerp.osv import fields as old_fields

class product_template(models.Model):
    _inherit = 'product.template'

    def _get_default_section_id(self):
        return self.env.user.default_section_id

    section_id = fields.Many2one('crm.case.section', 'Sales Team', default=_get_default_section_id)
    section_member_ids = fields.Many2many('res.users', 'Sales Team members', related='section_id.member_ids')
    section_public_categ_ids = fields.Many2many('product.public.category', related='section_id.public_categ_ids')

class crm_case_section(models.Model):
    _inherit = "crm.case.section"

    product_ids = fields.One2many('product.template', 'section_id', string='Products')
    website_description = fields.Html('Description for the website', translate=True)
    public_categ_ids = fields.Many2many('product.public.category', 'section_public_categ_rel', 'section_id', 'category_id', string='Allowed public categories', help='All child categories are also allowed automatically')

    sale_description = fields.Char('Sale description', help='This text is added to email for customer')

class res_users(models.Model):
    _inherit = 'res.users'

    section_ids = fields.Many2many('crm.case.section', 'sale_member_rel', 'member_id', 'section_id', 'Sales Team')

    def _get_group(self,cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_user')
            result.append(group_id)
            #dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_partner_manager')
            #result.append(group_id)
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result
    _defaults = {
        'groups_id': _get_group,
    }


class product_public_category(models.Model):
    _inherit = "product.public.category"

    section_ids = fields.Many2many('crm.case.section', 'section_public_categ_rel', 'category_id', 'section_id', string='Sales teams')

class sale_order(models.Model):
    _inherit = 'sale.order'

    parent_id = fields.Many2one('sale.order', 'Parent')
    child_ids = fields.One2many('sale.order', 'parent_id', 'Child orders')

    _track = {
        'state': {'website_sales_team.mt_order_created': lambda self, cr, uid, obj, ctx=None: obj.state in ['draft']}
    }
