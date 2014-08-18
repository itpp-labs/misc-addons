from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import tools
import logging
_logger = logging.getLogger(__name__)

import base64
import tempfile 


import MySQLdb
import MySQLdb.cursors

from pandas import DataFrame

from ..import_sugarcrm import import_sugarcrm
from ..import_kashflow import import_kashflow

import tarfile
import shutil

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import os
import glob

class sugarcrm_migration_upload(osv.TransientModel):
    _name = "sugarcrm_migration.upload"
    _description = "Upload dumps"

    _columns = {
        'sugarcrm_file': fields.char('Sugarcrm file (*.tar.gz)', help='Path on server'),
        'kashflow_file': fields.char('Kashflow file (*.tar.gz)', help='Path on server'),
        'db_host': fields.char('MySQL Host'),
        'db_port': fields.char('MySQL Port'),
        'db_name': fields.char('MySQL Database'),
        'db_user': fields.char('MySQL User'),
        'db_passwd': fields.char('MySQL Password'),
        }
    _defaults = {
        'db_host': 'localhost',
        'db_port': '3306',
        'db_name': 'test',
        'db_user': 'test',
        'db_passwd': 'test',
        }
    def upload_button(self, cr, uid, ids, context=None):

        record = self.browse(cr, uid, ids[0])

        self.kashflow(record, cr, uid)
        self.sugarcrm(record, cr, uid)

        return True

    def sugarcrm(self, record, cr, uid):
        #if not record.sugarcrm_file:
        #    return

        #unzip files
        files = []
        tmp_dir = None
        if record.sugarcrm_file:
            tmp_dir,files = self.unzip_file(record.sugarcrm_file.strip())

        instance = import_sugarcrm(self.pool, cr, uid,
                                   'sugarcrm', #instance_name
                                   'sugarcrm_migration', # module_name
                                   context={'db_host': record.db_host,
                                            'db_port': record.db_port,
                                            'db_user': record.db_user,
                                            'db_passwd': record.db_passwd,
                                            'db_name': record.db_name,
                                            'db_dump_fies': files
                                            }
                                   )
        try:
            shutil.rmtree(tmp_dir)
        except:
            pass
        
        instance.run()
        return instance

    def kashflow(self, record, cr, uid):
        if not record.kashflow_file:
            return

        # unzip files
        tmp,files = self.unzip_file(record.kashflow_file.strip(), pattern='*.csv')
        _logger.info('kashflow files: %s'%files)

        # map data and save to base_import.import
        instance = import_kashflow(self.pool, cr, uid,
                                   'kashflow', #instance_name
                                   'sugarcrm_migration', #module_name
                                   context = {'csv_files': files,
                                              'sugarcrm_instance_name':'sugarcrm'
                                              }
                                   )
        instance.run()
        return instance


    def unzip_file(self, filename, pattern='*'):
        '''
        extract *.tar.gz files

        returns list of extracted file names
        '''
        tar = tarfile.open(name=filename)
        dir = tempfile.mkdtemp(prefix='tmp_sugarcrm_migration')
        tar.extractall(path=dir)

        return dir, glob.glob('%s/%s' % (dir, pattern))+glob.glob('%s/*/%s' % (dir, pattern))
