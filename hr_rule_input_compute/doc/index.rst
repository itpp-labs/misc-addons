=======================
 Compute Salary Inputs
=======================

The module allows to make salary rule inputs as computable. A ``Python Code`` field in a salary rule form is editable for users with ``Enable to edit "Python Code" field for salary inputs`` group. The users can write code, which computes amounts of salary rule inputs, e.g.::

    inputs['COMPUTED_INPUT_FIRST']['amount'] = Python expression
    inputs['COMPUTED_INPUT_SECOND']['amount'] = Python expression

The amounts of the inputs will be computed after you set/change employee or period fields in payslips form.

Available variables:
* env: Odoo environment
* operator: Python standard library
* date_from: begin of employee payslip period, e.g. u'2017-03-01'
* date_to: end of employee payslip period, e.g. u'2017-03-30'
* inputs: dictionary with inputs data, e.g. {u'COMPUTED_INPUT_FIRST': {'code': u'COMPUTED_INPUT_FIRST', 'name': u'First Input', 'contract_id': 1}}

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

The module allows to make salary rule inputs as computable. The use of the module assumes you to have Python skills. For more details: https://apps.odoo.com/apps/modules/10.0/product_details/
