# -*- coding: utf-8 -*-
from . import im_notif_models


def pre_uninstall(cr, registry):
    query = ("UPDATE res_partner "
             "SET notify_email = 'always' "
             "WHERE notify_email LIKE 'im%';")
    cr.execute(query)
