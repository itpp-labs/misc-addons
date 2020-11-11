.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

=====================
 Preview Media Files
=====================

The module allows to open attachments (images and video (by default images only)) in popup
(for widget='image').

For doc, docx, xls, xlsx, pdf, youtube service, vimeo service support specify the media option as True
in xml and specify new invisible fields: media_type, media_video_ID, media_video_service.

eg for the model 'product.image'::

    <record model="ir.ui.view" id="view_product_image_form">
            <field name="name">product.image.form</field>
            <field name="model">product.image</field>
            <field name="inherit_id" ref="website_sale.view_product_image_form"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='image']" position="after">
                    <field name="media_type" invisible="1"/>
                    <field name="media_video_ID" invisible="1"/>
                    <field name="media_video_service" invisible="1"/>
                </xpath>
                <xpath expr="//field[@name='image']" position="attributes">
                    <attribute name="media">True</attribute>
                </xpath>
            </field>
        </record>

The Model should inherit the web_preview. In the '_preview_media_file' parameter specify the binary field
of the model.

eg for the model 'product.image' and the binary field 'image'::

    class ProductImage(models.Model):
        _name = 'product.image'
        _inherit = ['product.image', 'web.preview']

        _preview_media_file = 'image'

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* Dinar Gabbasov <gabbasov@it-projects.info>

      This module is not maintained since Odoo 12.0

Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/10.0/web_preview/

Tested on ``Odoo 10.0 <https://github.com/odoo/odoo/commit/<https://github.com/odoo/odoo/commit/852940f1ba1219b106590efc580ec2b5fdfa1740>`_>`_
