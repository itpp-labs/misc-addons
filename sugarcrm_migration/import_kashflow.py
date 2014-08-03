import MySQLdb
import MySQLdb.cursors
from import_base import import_base

from pandas import merge, DataFrame
from .mapper import *

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import csv

class import_kashflow(import_base):

    TABLE_ACCOUNT = 'accounts'

    def initialize(self):
        self.cvs_files = self.context.get('cvs_files')
        self.import_options.update({'separator':';',
                                    #'quoting':''
                                    })

    def get_data(self, table):
        file_name = filter(lambda f: f.endswith('/%s.txt' % table), this.cvs_files)[0]
        with open(file_name, 'rb') as csvfile:
            fixed_file = StringIO(csvfile.read()
                                  .replace('\r\r\n',' ')
                                  .replace('\r\n', '\n'))
        reader = csv.reader(fixed_file,
                            delimiter = self.import_options.get('separator'),
                            #quotechar = self.import_options.get('quoting'),
                            )
        return list(reader)

    def get_mapping(self):
        res = [
            self.get_mapping_account(),
        ]
        return res

    def get_mapping_account(self):
    def table_account(self):
        t1 = merge(DataFrame(self.get_data('accounts')),
                   DataFrame(self.get_data('accounts_cstm')),
                   left_index='id',
                   right_index='id_c'
        )
        #t1 = t1[:10] # TMP
        return t1
    def get_mapping_account(self):
        return {
            'name': self.TABLE_ACCOUNT,
            'table': self.table_account,
             'model' : 'res.partner',
             'dependencies' : [self.TABLE_USER],
             'map' : {
                'id': xml_id(self.TABLE_ACCOUNT, 'id'),
                 'name': concat('name', 'first_name_c', 'last_name_c'),
                'date': fixdate('date_entered'),
                'active': lambda record: not record['deleted'],
                 'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),
                 'website': first('website', 'website_c'),
                'phone':first('phone_office', 'telephone_c', 'company_phone_c', 'phone_primary_c'),
                'mobile':first('mobile_phone_primary_c', 'mobile_phone_other_c'),
                'email':first('email_c', 'email_primary_c', 'email_other_c'),
                'fax': first('phone_fax', 'fax_c', 'fax_primary_c'),
                 'ref': 'sic_code',
                 'customer': const('1'),
                 'supplier': const('0'),
                 'parent_id/id' : xml_id(self.TABLE_ACCOUNT, 'parent_id'),
    
    
                 'comment': ppconcat('description', 'employees', 'ownership')
                }
            }

