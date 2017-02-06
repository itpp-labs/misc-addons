========================
 Extra grouping options
========================

Usage
=====

* add this module to dependencies
* extend model you need, e.g.::

    class Sale(models.Model):
        _name = 'sale.order'
        _inherit = ['sale.order', 'base_groupby_extra']

* use groupby in views, e.g.::

    <filter string="Hour" context="{'group_by':'date:hour'}"/>

