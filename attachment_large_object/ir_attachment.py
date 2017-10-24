# -*- coding: utf-8 -*-
import logging
import base64
from odoo import models, api
import psycopg2

logger = logging.getLogger(__name__)

LARGE_OBJECT_LOCATION = 'postgresql:lobject'


class IrAttachment(models.Model):
    """Provide storage as PostgreSQL large objects of attachements with filestore location ``postgresql:lobject``.

    Works by overriding the storage handling methods of ``ir.attachment``, as intended by the
    default implementation. The overrides call :funct:`super`, so that this is transparent
    for other locations.
    """

    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    @api.model
    def lobject(self, cr, *args):
        return cr._cnx.lobject(*args)

    @api.model
    def _file_write(self, value, checksum):
        """Write the content in a newly created large object.

        :param value: base64 encoded payload
        :returns str: object id (will be considered the file storage name)
        """
        location = self._storage()
        if location != LARGE_OBJECT_LOCATION:
            return super(IrAttachment, self)._file_write(value, checksum)

        lobj = self.lobject(self.env.cr, 0, 'wb')  # oid=0 means creation
        lobj.write(base64.b64encode(value).decode())
        oid = lobj.oid
        return str(oid)

    def _file_delete(self, fname):
        filestore = False
        try:
            oid = int(fname)
        except:
            filestore = True

        if not filestore:
            try:
                return self.lobject(self.env.cr, oid, 'rb').unlink()
            except (psycopg2.OperationalError, ValueError):
                filestore = True

        return super(IrAttachment, self)._file_delete(fname)

    def _lobject_read(self, fname, bin_size):
        """Read the large object, base64 encoded.

        :param fname: file storage name, must be the oid as a string.
        """
        lobj = self.lobject(self.env.cr, int(fname), 'rb')
        if bin_size:
            return lobj.seek(0, 2)
        return base64.b64encode(lobj.read()) # GR TODO it must be possible to read-encode in chunks

    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        for attach in self:
            try:
                attach.datas = self._lobject_read(attach.store_fname, bin_size)
            except (psycopg2.OperationalError, ValueError):
                super(IrAttachment, attach)._compute_datas()
