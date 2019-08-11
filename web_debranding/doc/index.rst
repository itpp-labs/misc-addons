====================
 Backend debranding
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

By default the module replaces ``Odoo`` to ``Software``.

* Switch to Developer mode
* Open ``[[ General Settings ]] >> Technical >> Parameters >> System Parameters`` and modify:

  * ``web_debranding.new_title`` (put space in *Value field* if you don't need Brand in Title)
  * ``web_debranding.new_name`` (your Brand)
  * ``web_debranding.new_website`` (your website)
  * ``web_debranding.new_documentation_website`` (website with documentation instead of official one)
  * ``web_debranding.favicon_url``
  * ``web_debranding.send_publisher_warranty_url`` - set 0 to disable server requests to odoo.com and 1 otherwise (useful for enterprise contractors). Works only for non-enterprise versions of odoo, check `note <https://www.odoo.com/apps/modules/12.0/web_debranding/#enterprise-users-notice>`__ below.
  * ``web_debranding.icon_url`` - icon for mobile devices *recommended size :192x192*
  * ``web_debranding.apple_touch_icon_url`` - icon for IOS Safari *recommended size :152x152*

*Note. More user friendly way to configure the module is available in* `Brand Kit <https://apps.odoo.com/apps/modules/11.0/theme_kit/>`__.

Further debranding
==================

* Open *addons/mail/data/mail_data.xml* and edit Template **Notification Email** - delete ``using Odoo``
* Open *addons/website_livechat/data/website_livechat_data.xml* and edit in ``im_livechat_channel_data_website`` record *YourWebsiteWithOdoo.com* string
* Install `website_debranding <https://apps.odoo.com/apps/modules/11.0/website_debranding/>`__ if module *Website Builder* has been already installed in your system
* Install `pos_debranding <https://apps.odoo.com/apps/modules/11.0/pos_debranding/>`__ if module `POS` has been already installed in your system
* Delete *Odoo.com Accounts* record at *Settings\Users & Companies\OAuth Providers* if module ``OAuth2 Authentication`` has been already installed in your system
* To debrand ``/web/database/manager``:

  * edit *addons/web/views/database_manager.html* file:

    * delete or modify **<title>** tag
    * delete or modify favicon
    * delete or modify **<img>** tag with ``logo2.png``
    * delete or modify warning **<div class="alert alert-warning"> Warning, your Odoo database ...</div>**
    * delete or modify **<small class="text-muted">** To enhance your experience, some data may be sent to *Odoo online services*. See our `Privacy Policy <https://www.odoo.com/privacy>`__
    * delete or modify **<p class="form-text"> In order to avoid conflicts between databases, Odoo needs ...</p>**

Auto-debrand new databases
==========================

To automatically install this module for every new databases set 'auto_install': True in **__manifest__.py** files of following modules:

* ``web_debranding``
* ``ir_rule_protected``
* ``access_restricted``
* ``access_apps``
* ``access_settings_menu``
* ``mail (built-in)``
* ``base_setup (built-in)``
* ``bus (built-in)``

Usage
=====

* Open *Backend*

RESULT: Odoo is replaced to Your Brand in footer, Dialog Box, within phrases, empty messages, all backend qweb templates, hints, examples, Settings and Bot open menu (*Odoo Bot -> Bot*), etc.

Other debranded phrases can be found the following way ``[[ Settings ]] >> Translations >> Application Terms``.

The cases above, listed by way of the following examples: 

Examples
========

* The module deletes Odoo label in footer

    Powered by Odoo
    
* Search a random string at the menu ``[[ Settings ]] >> Users & Copanies >> Companies``
  
    Create and manage the companies that will be managed by Odoo from here. Shops or subsidiaries can be created and maintained from here.

* Remove Administrator via menu ``[[ Settings ]] >> Users & Copanies >> Users``
  
    You can not remove the admin user as it is used internally for resources created by Odoo (updates, module installation, ...).

* ``[[ Settings ]] >> Dashboard >> Companies``
* When you create new company it shows placeholder for field Website
  
    e.g. www.odoo.com

* Open menu``[[ Settings ]] >> General Settings``.

    Use external pads in Odoo Notes. 
    Extract and analyze Odoo data from Google Spreadsheet.

* Open menu ``[[ Settings ]] >> Dashboard >> *Implementation* section``
  
    Follow these implementation guides to get the most out of Odoo.

* Open menu ``[[ Discuss ]] >> CHANNELS >> #general``
* Send ``/help`` to the chat

    OdooBot - now

    You are in channel #general.

    You can mention someone by typing @username, this will grab its attention.
    
    You can mention a channel by typing #channel.
    
    You can execute a command by typing /command.
    
    You can insert canned responses in your message by typing :shortcut.

