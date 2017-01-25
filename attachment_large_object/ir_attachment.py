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

    def _file_write(self, cr, uid, value):
        """Write the content in a newly created large object.

        :param value: base64 encoded payload
        :returns str: object id (will be considered the file storage name)
        """
        location = self._storage(cr, uid)
        if location != LARGE_OBJECT_LOCATION:
            return super(IrAttachment, self)._file_write(cr, uid, value)

        lobj = self.lobject(cr, 0, 'wb')  # oid=0 means creation
        lobj.write(value.decode('base64'))
        oid = lobj.oid
        return str(oid)

    def _lobject_delete(self, cr, uid, fname):
        """Delete the large object.

        :param fname: file storage name, must be the oid as a string.
        """
        try:
            oid = long(fname)
        except:
            # it means there is a legacy attachment
            self._file_delete(cr, uid, fname)
        else:
            self.lobject(cr, oid, 'rb').unlink()

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

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self._storage(cr, uid, context)
        file_size = len(value.decode('base64'))
        attach = self.browse(cr, uid, id, context=context)
        fname_to_delete = attach.store_fname
        if location != 'db':
            fname = self._file_write(cr, uid, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            vals = {
                'store_fname': fname,
                'file_size': file_size,
                'db_datas': False,
            }
            super(IrAttachment, self).write(cr, SUPERUSER_ID, [id], vals, context=context)
        else:
            super(IrAttachment, self).write(
                cr, SUPERUSER_ID, [id],
                {'db_datas': value, 'file_size': file_size, 'store_fname': False},
                context=context)

        # ugly but the write delete the file_size entry
        query = 'update %s set file_size=%%s where id = %%s' % self._table
        cr.execute(query, (file_size, id))

        # After de-referencing the file in the database, check whether we need
        # to garbage-collect it on the filesystem
        if fname_to_delete:
            try:
                self._lobject_delete(cr, uid, fname_to_delete)
            except (psycopg2.OperationalError, ValueError):
                self._file_delete(cr, uid, fname_to_delete)
        return True

    _columns = {
        'datas': fields.function(
            _data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }

    def create(self, cr, uid, values, context=None):
        # ugly but correct a base module
        if 'file_size' in values:
            del values['file_size']

        return super(IrAttachment, self).create(cr, uid, values, context=context)
