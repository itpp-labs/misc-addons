# -*- coding: utf-8 -*-
import logging
from openerp import SUPERUSER_ID, models, api
_logger = logging.getLogger(__name__)

MODULE = '_web_debranding'


class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _create_debranding_views(self):

        self._create_view('menu_secondary', 'web.menu_secondary', '''
        <xpath expr="//div[@class='oe_footer']" position="replace">
           <div class="oe_footer"></div>
       </xpath>''')

        self._create_view('webclient_bootstrap_enterprise_title', 'web.webclient_bootstrap', '''
       <xpath expr="//title" position="replace"></xpath>''')

        self._create_view('webclient_bootstrap_enterprise_favicon', 'web.webclient_bootstrap', '''
       <xpath expr="//link[@rel='shortcut icon']" position="replace">
           <t t-set="favicon" t-value="request and request.env['ir.config_parameter'].get_param('web_debranding.favicon_url', '').strip() or ''"/>
           <t t-if="favicon">
               <link rel="shortcut icon" t-att-href="favicon" type="image/x-icon"/>
           </t>
       </xpath>''')

    @api.model
    def _create_view(self, name, inherit_id, arch, noupdate=False, type='qweb'):
        view = self.env.ref("%s.%s" % (MODULE, name), raise_if_not_found=False)
        if view:
            try:
                view.write({
                    'arch': arch,
                })
            except:
                _logger.warning('Cannot update view %s. Delete it.', name, exc_info=True)
                view.unlink()
                return

            return view.id

        try:
            with self.env.cr.savepoint():
                view = self.env['ir.ui.view'].create({
                    'name': name,
                    'type': type,
                    'arch': arch,
                    'inherit_id': self.env.ref(inherit_id, raise_if_not_found=True)
                })
        except:
            _logger.debug('Cannot create view %s. Cancel.', name, exc_info=True)
            return
        self.env['ir.model.data'].create({
            'name': name,
            'model': 'ir.ui.view',
            'module': MODULE,
            'res_id': view.id,
            'noupdate': noupdate,
        })
        return view.id
