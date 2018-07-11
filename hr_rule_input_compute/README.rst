=======================
 Compute Salary Inputs
=======================

The module allows to make salary rule inputs as computable. The ``Python Code`` field in a salary rule form is editable for users with ``Enable to edit "Python Code" field for salary inputs`` group. The users can write the code which computes amounts of salary rule inputs, e.g.::

    inputs['COMPUTED_INPUT_FIRST']['amount'] = Python expression
    inputs['COMPUTED_INPUT_SECOND']['amount'] = Python expression

The amounts of the inputs will be computed after you set/change employee or period fields in payslips form.

Available variables:

* env: Odoo environment
* operator: Python standard library
* date_from: begin of employee payslip period, e.g. u'2017-03-01'
* date_to: end of employee payslip period, e.g. u'2017-03-30'
* inputs: dictionary with inputs data, e.g. {u'COMPUTED_INPUT_FIRST': {'code': u'COMPUTED_INPUT_FIRST', 'name': u'First Input', 'contract_id': 1}}

Credits
=======

Contributors
------------
* Stanislav Krotov <krotov@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/11.0/hr_rule_input_compute/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/11.0

HTML Description: https://apps.odoo.com/apps/modules/11.0/hr_rule_input_compute/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 11.0 8787f5acee9b5d2cad15b97804522dc04717a1c1
