# -*- coding: utf-8 -*-
import logging
from openerp import models, SUPERUSER_ID
from openerp.osv import fields
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

    def lobject(self, cr, *args):
        return cr._cnx.lobject(*args)

    def _file_write(self, cr, uid, value, checksum):
        """Write the content in a newly created large object.

        :param value: base64 encoded payload
        :returns str: object id (will be considered the file storage name)
        """
        location = self._storage(cr, uid)
        if location != LARGE_OBJECT_LOCATION:
            return super(IrAttachment, self)._file_write(cr, uid, value, checksum)

        lobj = self.lobject(cr, 0, 'wb')  # oid=0 means creation
        lobj.write(value.decode('base64'))
        oid = lobj.oid
        return str(oid)

    def _file_delete(self, cr, uid, fname):
        filestore = False
        try:
            oid = long(fname)
        except:
            filestore = True

        if not filestore:
            try:
                return self.lobject(cr, oid, 'rb').unlink()
            except (psycopg2.OperationalError, ValueError):
                filestore = True

        return super(IrAttachment, self)._file_delete(cr, uid, fname)

    def _lobject_read(self, cr, uid, fname, bin_size):
        """Read the large object, base64 encoded.

        :param fname: file storage name, must be the oid as a string.
        """
        lobj = self.lobject(cr, long(fname), 'rb')
        if bin_size:
            return lobj.seek(0, 2)
        return lobj.read().encode('base64')  # GR TODO it must be possible to read-encode in chunks

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            try:
                result[attach.id] = self._lobject_read(cr, uid, attach.store_fname, bin_size)
            except (psycopg2.OperationalError, ValueError):
                if attach.store_fname:
                    result[attach.id] = self._file_read(cr, uid, attach.store_fname, bin_size)
                else:
                    result[attach.id] = attach.db_datas
        return result

    def _data_set(self, *args, **kwargs):
        return super(IrAttachment, self)._data_set(*args, **kwargs)

    _columns = {
        'datas': fields.function(
            _data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }
