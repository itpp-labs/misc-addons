# -*- coding: utf-8 -*-
import openerp


def post_load():
    if not openerp.tools.config.get('log_db'):
        if openerp.tools.config.get('test_enable') or openerp.tools.config.get('stop_after_init'):
            # TODO make autotests and instruct travis to run odoo with required parameters
            return
        raise openerp.exceptions.UserError(
            'You have to define a log_db value in the config to use the'
            'Postgres Session Store.')

    from . import http
