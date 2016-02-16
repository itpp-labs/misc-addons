# -*- coding: utf-8 -*-

from . import controllers
from openerp import SUPERUSER_ID


def init_auth(cr, registry):
    icp = registry['ir.config_parameter']
    icp.set_param(cr, SUPERUSER_ID, 'auth_signup.allow_uninvited', True)
