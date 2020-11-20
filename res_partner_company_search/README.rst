.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

Search partner by company fields. It uses only related fields like this:

    p_FIELD_NAME = fields.TYPE(related='parent_id.FIELD_NAME', string='Parent FIELD')

Check models.py file to find list of related fields.

Technically modules updates search domain as follows:

    [..., ('category_id', OPERATOR, VALUE), ...]

    ->

    [..., '|', ('p_category_id', OPERATOR, VALUE), ('category_id', OPERATOR, VALUE), ...]

Tested on `Odoo 8.0 <https://github.com/odoo/odoo/commit/ea60fed97af1c139e4647890bf8f68224ea1665b>`_

Further information and discussion: https://yelizariev.github.io/odoo/module/2015/02/26/company-contacts.html

* `IT-Projects LLC <https://it-projects.info>`__

  The module is not maintained since Odoo 9.0.
