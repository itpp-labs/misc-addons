# -*- coding: utf-8 -*-

from openerp import models


class ProjectDefaultVisibilityFollowers(models.Model):
    _inherit = 'project.project'
    _defaults = {'privacy_visibility': 'followers'}
