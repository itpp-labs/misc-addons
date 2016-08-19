# -*- coding: utf-8 -*-

from openerp import models, fields, api


class project_default_visibility_followers(models.Model):
    _inherit = 'project.project'
    _defaults = {'privacy_visibility': 'followers'}
