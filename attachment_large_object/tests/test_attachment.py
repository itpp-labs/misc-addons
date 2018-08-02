import base64

from openerp.tests.common import TransactionCase


class TestAttachment(TransactionCase):

    def setUp(self):
        super(TestAttachment, self).setUp()
        self.attachment = self.env['ir.attachment']
        self.param = self.env['ir.config_parameter']

    def test_large_object(self):
        self.param.set_param('ir_attachment.location', 'postgresql:lobject')
        bin_data = base64.b64encode(b"\xff data")
        att = self.attachment.create(dict(name="some name", datas=bin_data))

        # check payload and the fact that 'store_fname' looks like a PG oid
        att_r = att.read(('datas', 'store_fname', 'file_size'))
        if isinstance(att_r, (list, tuple)):
            att_r = att_r[0]
        self.assertEqual(att_r['datas'], bin_data)
        self.assertEqual(att_r['file_size'], 6)
        try:
            oid = int(att_r['store_fname'])
        except TypeError:
            self.fail("We had a non regular oid: %r. Large object not actually called ?")

        # writing without touching the payload does not create a new large object
        att.write(dict(name="new name"))
        record = self.attachment.browse(att.id)
        self.assertEqual(record.store_fname, str(oid))

        # a write on data, creates a whole new large object
        att.write(dict(datas=base64.b64encode(b'new content')))
        att_r = att.read(('datas', 'store_fname'))
        if isinstance(att_r, (list, tuple)):
            att_r = att_r[0]
        self.assertNotEqual(att_r['store_fname'], str(oid))

        att.unlink()
