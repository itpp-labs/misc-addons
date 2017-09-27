# -*- coding: utf-8 -*-
import logging

from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestDataGet(TransactionCase):
    at_install = False
    post_install = True

    def test_data_get(self):
        _logger.info('in test_data_get')
        users = self.env['res.users'].search_read([], ['id', 'image_medium'])
