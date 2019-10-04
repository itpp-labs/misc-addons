===============================================
 Context-dependent values in System Parameters
===============================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Make database backup (or at least ``ir.config_parameter`` table)

Configuration
=============

* Open menu ``[[ Settings ]] >> General Settings``
* Activate **[x] Multi Company - Manage multiple companies**
* Click ``[Apply]``
* Open menu ``[[ Settings ]] >> Users & Companies >> Users``
* Select your user
* Add some companies to **Allowed Companies** field

Usage
=====

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Technical >> Parameters >> System Parameters``
* Choose some record or create new one
* Set some value
* Switch your user to another company

  * Click top right-hand button with your user name
  * Click ``Preferences``
  * Set new value for **Company** field
  * Click ``[Save]``

* Set new value for the System Parameter record
* Switch back to previous company
* RESULT: Value of the System Parameter depends on current company 

Default values
--------------

All system parameters created before module installation (as well as just created parameters) become default value for corresponding parameters. Example:

* Before installation:

  * **param1** = *value1*
  * **param2** = *value2*

* After installation:

  * **param1** = *value1* -- default value for param1
  * **param2** = *value2* -- default value for param2

* Now if we switch to companyA and make following updates:

  * **param1** = *value11*

* And if we switch to companyB and make following updates:

  * **param2** = *value22*
  * **param3** = *value3*

* Then for companyA we have

  * **param1** = *value11* (value for companyA)
  * **param2** = *value2* (default value)
  * **param3** = *value3* (default value)

* Then for companyB we have

  * **param1** = *value1* (via default value)
  * **param2** = *value22* (value for companyB)
  * **param3** = *value3* (via default value)

For understanding how multi-website values work see Documentation of `web_website <https://apps.odoo.com/apps/modules/13.0/web_website/>`__

Company Properties
------------------

For understanding which values are default and which are company dependent do as following:

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Technical >> Parameters >> Company Properties``
* Click ``[Group By] -> Field``
* Now you can find all records under ``Value (ir.config_parameter)``

Protected properties
--------------------

Following parameter is shared across all companies wherever it was changed:

* ``database.expiration_date`` -- it's used in Odoo EE


Reseting value for all companies
--------------------------------

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Go to ``[[ Settings ]] >> Technical >> Parameters >> Company Properties``
* Group records by ``Resource``
* Find group ``ir.config_parameter,<ID>`` for the Parameter you need. To get ID of the parameter do as following

  * Go to ``[[ Settings ]] >> Technical >> Parameters >> System Parameters``
  * Open the Parameter you need
  * Check url of the page. It contains id value. In example below id is 3 
    
        /web?debug#id=3&view_type=form&model=ir.config_parameter&menu_id=25&action=9
* Select all values in the group except defaul one. Click ``[Action] -> Delete``. Don't do anything if you have default value only.
* Open default value and change the value if needed 
* Go to ``[[ Settings ]] >> Technical >> Parameters >> System Parameters``
* Check that the value for each company is reset and it matches the default value.

Uninstallation
==============

On uninstallation parameter values are restored to *Default values* (see above).
Nevertheless, it's recommended to follow steps below, if you are not sure, that
those values are ones you need.

* It's recommended to make database backup before uninstallating the module
* Open menu ``[[ Settings ]] >> Technical >> Parameters >> System Parameters``
* Make Export of all records (``[Action] -> Export``) -- exporting only column ``value`` is enough.
* Click ``[Import]`` button
* Upload ``*.csv`` file
* Click ``[Validate]`` -- it may take some time. It must not return errors!
* Don't close current page!
* Uninstall the module at another page
* Return back to page with importing
* Click ``[Import]``

