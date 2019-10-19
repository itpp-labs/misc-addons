Add a new widget named "polymorphic"
The polymorphic field allow to dynamically store an id linked to any model in
Odoo instead of the usual fixed one in the view definition

E.g::

    <field name="model" widget="polymorphic" polymorphic="object_id" />
    <field name="object_id" />

Maintainers
------------
This module is not maintainable since Odoo 11.0, because lack of interests from customers.
