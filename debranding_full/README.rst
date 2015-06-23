Full Debranding
===============

Removes references to odoo.

disable_openerp_online
----------------------

The module depends on *disable_openerp_online* module from that repository: https://github.com/OCA/server-tools

website_debranding
------------------

The module depends on *website_debranding* module from that repository: https://github.com/yelizariev/website-addons

im_odoo_support
---------------

**im_odoo_support** should be disabled and uninstalled manually:

1. open *\_\_openerp__.py* file of im_odoo_support module and set autoinstall option to False. Also, you can do it via *sed* tool:

    cd path/to/odoo
	sed -i "s/'auto_install': True/'auto_install': False/" addons/im_odoo_support/__openerp__.py

2. update modules list

3. uninstall im_odoo_support from odoo

