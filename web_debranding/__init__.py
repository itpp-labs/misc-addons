# -*- coding: utf-8 -*-
from . import models
from . import controllers
from . import fields

from openerp import SUPERUSER_ID

MODULE = '_web_debranding'


def uninstall_hook(cr, registry):
    registry['ir.model.data']._module_data_uninstall(cr, SUPERUSER_ID, [MODULE])
