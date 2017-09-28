# -*- coding: utf-8 -*-
import logging

from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestDataGet(TransactionCase):
    at_install = False
    post_install = True

    def test_data_get(self):
        users = self.env['res.users'].search_read([], ['id', 'image_medium'])
        test_attachment = self.env.ref('ir_attachment_url.test_url_attachment')
        datas = self.env['ir.attachment'].search_read([("id", "=", test_attachment.id)], ['id', 'datas'])
