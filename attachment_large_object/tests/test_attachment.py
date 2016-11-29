# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestAttachment(TransactionCase):

    def setUp(self):
        super(TestAttachment, self).setUp()
        self.attachment = self.registry('ir.attachment')
        self.param = self.registry('ir.config_parameter')

    def test_large_object(self):
        cr, uid, att = self.cr, self.uid, self.attachment
        self.param.set_param(
            cr, self.uid, 'ir_attachment.location', 'postgresql:lobject')
        bin_data = "\xff data".encode('base64')
        att_id = att.create(cr, uid, dict(name="some name", datas=bin_data))

        # check payload and the fact that 'store_fname' looks like a PG oid
        att_r = att.read(cr, uid, att_id, ('datas', 'store_fname', 'file_size'))
        if isinstance(att_r, (list, tuple)):
            att_r = att_r[0]
        self.assertEqual(att_r['datas'], bin_data)
        self.assertEqual(att_r['file_size'], 6)
        try:
            oid = long(att_r['store_fname'])
        except TypeError:
            self.fail("We had a non regular oid: %r. Large object not actually called ?")

        # writing without touching the payload does not create a new large object
        att.write(cr, uid, att_id, dict(name="new name"))
        record = att.browse(cr, uid, att_id)
        self.assertEqual(record.store_fname, unicode(oid))

        # a write on data, creates a whole new large object
        att.write(cr, uid, att_id, dict(datas='new content'.encode('base64')))
        att_r = att.read(cr, uid, att_id, ('datas', 'store_fname'))
        if isinstance(att_r, (list, tuple)):
            att_r = att_r[0]
        self.assertNotEqual(att_r['store_fname'], unicode(oid))

        att.unlink(cr, uid, att_id)
