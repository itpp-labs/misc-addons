from openerp import api,models,fields

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

class res_users(models.Model):
    _inherit = 'res.users'

    section_ids = fields.Many2many('crm.case.section', 'sale_member_rel', 'member_id', 'section_id', 'Sales Team')

class product_public_category(models.Model):
    _inherit = "product.public.category"

    section_ids = fields.Many2many('crm.case.section', 'section_public_categ_rel', 'category_id', 'section_id', string='Sales teams')
