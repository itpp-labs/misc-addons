.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

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

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* Stanislav Krotov <krotov@it-projects.info>


Further information
===================

Odoo Apps Store https://apps.odoo.com/apps/modules/11.0/hr_rule_input_compute/


Tested on `Odoo 11.0 <https://github.com/odoo/odoo/commit/8787f5acee9b5d2cad15b97804522dc04717a1c1>`_
