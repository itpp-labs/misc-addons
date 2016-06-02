
from openerp import SUPERUSER_ID, models, tools, api

MODULE = '_web_debranding'

class view(models.Model):
    _inherit = 'ir.ui.view'

    def _create_debranding_views(self, cr, uid):

        self._create_view(cr, uid, 'menu_secondary', 'web.menu_secondary', '''
        <xpath expr="//div[@class='oe_footer']" position="replace">
           <div class="oe_footer"></div>
       </xpath>''')

        self._create_view(cr, uid, 'webclient_bootstrap_enterprise_title', 'web.webclient_bootstrap', '''
       <xpath expr="//title" position="replace"></xpath>''')

        self._create_view(cr, uid, 'webclient_bootstrap_enterprise_favicon', 'web.webclient_bootstrap', '''
       <xpath expr="//link[@rel='shortcut icon']" position="replace">
           <t t-set="favicon" t-value="request and request.env['ir.config_parameter'].get_param('web_debranding.favicon_url', '').strip() or ''"/>
           <t t-if="favicon">
               <link rel="shortcut icon" t-att-href="favicon" type="image/x-icon"/>
           </t>
       </xpath>''')

    def _create_view(self, cr, uid, name, inherit_id, arch, noupdate=False, type='qweb'):
        registry = self.pool
        view_id = registry['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, "%s.%s" % (MODULE, name))
        if view_id:
            registry['ir.ui.view'].write(cr, SUPERUSER_ID, [view_id], {
                'arch': arch,
            })
            return view_id

        try:
            view_id = registry['ir.ui.view'].create(cr, SUPERUSER_ID, {
                'name': name,
                'type': type,
                'arch': arch,
                'inherit_id': registry['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, inherit_id, raise_if_not_found=True)
            })
        except:
            import traceback
            traceback.print_exc()
            return
        registry['ir.model.data'].create(cr, SUPERUSER_ID, {
            'name': name,
            'model': 'ir.ui.view',
            'module': MODULE,
            'res_id': view_id,
            'noupdate': noupdate,
        })
        return view_id
