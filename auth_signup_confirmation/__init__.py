# -*- coding: utf-8 -*-

from . import controllers
from openerp import api, SUPERUSER_ID


def init_auth(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    icp = env['ir.config_parameter']

    icp.set_param('auth_signup.allow_uninvited', True)
