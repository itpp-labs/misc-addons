# -*- coding: utf-8 -*-
from odoo import models, fields, api


class S3Settings(models.TransientModel):
    _name = 's3.config.settings'
    _inherit = 'res.config.settings'

    s3_bucket = fields.Char(string='S3 bucket name', help="i.e. 'attachmentbucket'")
    s3_access_key_id = fields.Char(string='S3 access key id')
    s3_secret_key = fields.Char(string='S3 secret key')
    s3_condition = fields.Char(string='S3 condition',
                               help="""Specify valid odoo search domain here,
                               i.e. [('res_model', 'in', ['product.image'])].
                               According to this only data of model product.image will be sored on S3""")

    # s3_bucket
    @api.model
    def get_default_s3_bucket(self, fields):
        s3_bucket = self.env["ir.config_parameter"].get_param("s3.bucket")
        return {'s3_bucket': s3_bucket or False}

    def set_s3_bucket(self):
        self.env['ir.config_parameter'].set_param("s3.bucket",
                                                  self.s3_bucket or '',
                                                  groups=['base.group_system'])

    # s3_access_key_id
    @api.model
    def get_default_s3_access_key_id(self, fields):
        s3_access_key_id = self.env["ir.config_parameter"].get_param("s3.access_key_id")
        return {'s3_access_key_id': s3_access_key_id or False}

    def set_s3_access_key_id(self):
        self.env['ir.config_parameter'].set_param("s3.access_key_id",
                                                  self.s3_access_key_id or '',
                                                  groups=['base.group_system'])

    # s3_secret_key
    @api.model
    def get_default_s3_secret_key(self, fields):
        s3_secret_key = self.env["ir.config_parameter"].get_param("s3.secret_key")
        return {'s3_secret_key': s3_secret_key or False}

    def set_s3_secret_key(self):
        self.env['ir.config_parameter'].set_param("s3.secret_key",
                                                  self.s3_secret_key or '',
                                                  groups=['base.group_system'])

    # s3_condition
    @api.model
    def get_default_s3_condition(self, fields):
        s3_condition = self.env["ir.config_parameter"].get_param("s3.condition")
        return {'s3_condition': s3_condition or False}

    def set_s3_condition(self):
        self.env['ir.config_parameter'].set_param("s3.condition",
                                                  self.s3_condition or '',
                                                  groups=['base.group_system'])
