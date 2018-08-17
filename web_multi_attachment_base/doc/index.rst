=============================
 Upload Multiple Attachments
=============================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

To use this module add a model for attachments and specify the attribute **drop_attachments_field = '1'** into the corresponding kanban view.

For example::

        <field name="something_image_ids" mode="kanban">
            <kanban string="Something Images"
                    drop_attachments_field='1'>
                <field name="name"/>
                <field name="image" />

                ...

            </kanban>
        </field>

Where something_image_ids is a One2many field to the model with images.
