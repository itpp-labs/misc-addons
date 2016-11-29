# -*- coding: utf-8 -*-

import logging
from openerp.osv import osv

logger = logging.getLogger(__name__)

LARGE_OBJECT_LOCATION = 'postgresql:lobject'


class IrAttachment(osv.Model):
    """Provide storage as PostgreSQL large objects of attachements with filestore location ``%r``.

    Works by overriding the storage handling methods of ``ir.attachment``, as intended by the
    default implementation. The overrides call :funct:`super`, so that this is transparent
    for other locations.
    """ % LARGE_OBJECT_LOCATION

    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    def lobject(self, cr, *args):
        return cr._cnx.lobject(*args)

    def _file_write(self, cr, uid, location, value):
        """Write the content in a newly created large object.

        :param value: base64 encoded payload
        :returns str: object id (will be considered the file storage name)
        """

        if location != LARGE_OBJECT_LOCATION:
            return super(IrAttachment, self)._file_write(cr, uid, location, value)

        lobj = self.lobject(cr, 0, 'wb')  # oid=0 means creation
        lobj.write(value.decode('base64'))
        oid = lobj.oid
        return str(oid)

    def _file_delete(self, cr, uid, location, fname):
        """Delete the large object.

        :param fname: file storage name, must be the oid as a string.
        """
        if location != LARGE_OBJECT_LOCATION:
            return super(IrAttachment, self)._file_delete(cr, uid, location, fname)

        self.lobject(cr, long(fname), 'rb').unlink()

    def _file_read(self, cr, uid, location, fname, bin_size=False):
        """Read the large object, base64 encoded.

        :param fname: file storage name, must be the oid as a string.
        """
        if location != LARGE_OBJECT_LOCATION:
            return super(IrAttachment, self)._file_read(cr, uid, location, fname, bin_size=bin_size)

        lobj = self.lobject(cr, long(fname), 'rb')
        if bin_size:
            return lobj.seek(0, 2)
        return lobj.read().encode('base64')  # GR TODO it must be possible to read-encode in chunks


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
