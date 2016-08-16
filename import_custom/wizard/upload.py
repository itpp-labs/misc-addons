# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import logging
_logger = logging.getLogger(__name__)

import tempfile


try:
    import MySQLdb
    import MySQLdb.cursors
    from pandas import DataFrame

except ImportError:
    pass

from ..import_custom import import_custom

import tarfile
import shutil

try:
    from cStringIO import StringIO
except ImportError:
    pass

import glob


class ImportCustomUpload(osv.TransientModel):
    _name = "import_custom.upload"
    _description = "Upload dumps"

    _columns = {
        'file': fields.char('file (*.tar.gz)'),
    }

    def upload_button(self, cr, uid, ids, context=None):

        record = self.browse(cr, uid, ids[0])

        tmp_dir, files = self.unzip_file(record.file.strip(), pattern='*.csv')
        _logger.info('files: %s' % files)

        instance = import_custom(self.pool, cr, uid,
                                 'yelizariev',  # instance_name
                                 'import_custom',  # module_name
                                 run_import=False,
                                 import_dir='/home/tmp/',
                                 context={'csv_files': files},
                                 )

        instance.run()

        try:
            shutil.rmtree(tmp_dir)
        except:
            pass

        return instance

    def unzip_file(self, filename, pattern='*'):
        '''
        extract *.tar.gz files

        returns list of extracted file names
        '''
        tar = tarfile.open(name=filename)
        dir = tempfile.mkdtemp(prefix='tmp_import_custom')
        tar.extractall(path=dir)

        return dir, glob.glob('%s/%s' % (dir, pattern)) + glob.glob('%s/*/%s' % (dir, pattern))
