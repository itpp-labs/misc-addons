# -*- coding: utf-8 -*-
import logging
import os
_logger = logging.getLogger(__name__)
try:
    import MySQLdb
    import MySQLdb.cursors
except ImportError:
    pass

from openerp.addons.import_framework.import_base import import_base

try:
    from pandas import merge, DataFrame
except ImportError:
    pass

from openerp.addons.import_framework.mapper import *

import re

import time
import datetime as DT

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import csv

import glob
from openerp.osv.fields import sanitize_binary_value

class fixdate_custom(mapper):
    """
    convert '2010/12/31 13:26:25' to '2010-12-31'
    """
    def __init__(self, field_name):
        self.field_name = field_name
        
    def __call__(self, external_values):
        s = external_values.get(self.field_name)
        if not s:
            return ''
        m,d,y = str(s).split(' ')[0].split('/')
        return '20%s-%s-%s' % (y,m,d)

class image(mapper):
    def __init__(self, val):
        self.val = val

    def __call__(self, external_values):
        val = external_values.get(self.val)
        files = glob.glob('/home/tmp/thumbs/%s_*' % val)

        max_file = None
        max_size = 0
        for f in files:
            size = os.path.getsize(f)
            if size > 93000:
                continue

            if size < max_size:
                continue

            max_size = size
            max_file = f

        if not max_file:
            return None
        with open(max_file, 'r') as f:
            b = f.read()

        val = sanitize_binary_value(b)
        return val


class import_custom(import_base):
    TABLE_PROSPECTS = 'prospects_burda'
    TABLE_PROSPECTS_TAG = TABLE_PROSPECTS + '_tag'

    TABLE_PRODUCT = 'products'
    TABLE_PRODUCT_CATEGORY = 'categories'

    COL_LINE_NUM = 'line_num'

    def initialize(self):
        self.csv_files = self.context.get('csv_files')
        self.import_options.update({'separator':',',
                                    #'quoting':''
                                    })
    def get_data(self, table):
        file_name = filter(lambda f: f.endswith('/%s.csv' % table), self.csv_files)
        if file_name:
            _logger.info('read file "%s"' % ( '%s.csv' % table))
            file_name = file_name[0]
        else:
            _logger.info('file not found %s' % ( '%s.csv' % table))
            return []

        with open(file_name, 'rb') as csvfile:
            fixed_file = StringIO(csvfile.read() .replace('\r\n', '\n'))
        reader = csv.DictReader(fixed_file,
                            delimiter = self.import_options.get('separator'),
                            #quotechar = self.import_options.get('quoting'),
                            )
        res = list(reader)
        for line_num, line in enumerate(res):
            line[self.COL_LINE_NUM] = str(line_num)
        return res
    def get_mapping(self):
        return [
            self.get_mapping_partners(),
            self.get_mapping_product_categories(),
            self.get_mapping_products(),
        ]

    def get_table(self, table):
        def f():
            t = DataFrame(self.get_data(table))
            #t = t[:10] # for debug
            return t
        return f

    def get_hook_tag(self, field_name):
        def f(external_values):
            res = []
            value = external_values.get(field_name)
            value = value or ''
            if not isinstance(value, basestring):
                value = str(value)
            for v in value.split(','):
                #v = do_clean_sugar(v)
                if v:
                    res.append({field_name:v})
            return res
        return f

    def tag(self, model, xml_id_prefix, field_name):
        parent = xml_id_prefix + field_name
        return {'model':model,
                'hook':self.get_hook_tag(field_name),
                 'fields': {
                    'id': xml_id(parent, field_name),
                    'name': field_name,
                     #'parent_id/id':const('sugarcrm_migration.'+parent),
                    }
                }

    def get_mapping_partners(self):
        return {
            'name': self.TABLE_PROSPECTS,
            'table': self.get_table(self.TABLE_PROSPECTS),
            'dependencies' : [],
            'models':[
                self.tag('res.partner.category', self.TABLE_PROSPECTS_TAG, 'Tag'),
                self.tag('res.partner.category', self.TABLE_PROSPECTS_TAG, 'Tags'),
                self.tag('res.partner.category', self.TABLE_PROSPECTS_TAG, 'TypeName'),
                {'model' : 'res.partner',
                 'fields': {
                     'id': xml_id(self.TABLE_PROSPECTS, 'External ID'),
                     'name': 'Name',
                     'lang': const('es_ES'),
                     'is_company': map_val('Is a Company', {'True':'1', 'False':'0'}, default='0'),
                     'customer': const('1'),
                     'supplier': const('0'),
                     'category_id/id': tags_from_fields(self.TABLE_PROSPECTS_TAG, ['Tag','Tags', 'TypeName']),
                     'street': 'Street',
                     'street2': 'Street2',
                     'zip': 'Zip',
                     'city': 'City',
                     'phone': 'Phone',
                     'mobile': 'Mobile',
                     'email': 'Email',
                     'country_id/.id': country_by_name('Country'),
                     'date': fixdate_custom('CreationDate'),
                     'comment': ppconcat('Subscription'),
                     }
                 },
                {'model' : 'res.partner',
                 'hook': self.get_hook_ignore_empty('ContactLastname', 'ContactEmail'),
                 'fields': {
                     'id': xml_id(self.TABLE_PROSPECTS+'_child', 'External ID'),
                     'parent_id/id': xml_id(self.TABLE_PROSPECTS, 'External ID'),
                     'name': concat('ContactTitle', 'ContactFirstname', 'ContactLastname', delimiter=' '),
                     'customer': const('1'),
                     'supplier': const('0'),
                     'function': 'ContactJobtitle',
                     'phone': 'ContactPhone',
                     'fax': 'ContactFax',
                     'email': 'ContactEmail',
                     'lang': const('es_ES'),
                     'comment': ppconcat('ContactGender'),
                     }
                 }
                ]
            }
    def get_mapping_product_categories(self):
        return {
            'name': self.TABLE_PRODUCT_CATEGORY,
            'table': self.get_table(self.TABLE_PRODUCT_CATEGORY),
            'dependencies' : [],
            'models':[
                {'model' : 'product.public.category',
                 'fields': {
                     'id': xml_id(self.TABLE_PRODUCT_CATEGORY, 'id'),
                     'name': 'label',
                 },
                },
                {'model' : 'product.public.category',
                 'hook': lambda vals: vals.get('parent_id')!='NULL' and vals or None,
                 'fields': {
                     'id': xml_id(self.TABLE_PRODUCT_CATEGORY, 'id'),
                     'name': 'label',
                     'parent_id/id': xml_id(self.TABLE_PRODUCT_CATEGORY, 'parent_id'),
                 },
                },
             ]
        }
    def table_product(self):
        t = DataFrame(self.get_data('ecom_items'))
        t = merge(t,
                  DataFrame(self.get_data('ecom_items_ref')),
                  how='left',
                  left_on='ID',
                  suffixes=('', '_ref'),
                  right_on='ecom_items_id')
        t = merge(t,
                  DataFrame(self.get_data('item_categories')),
                  how='left',
                  left_on='ID',
                  suffixes=('', '_categories'),
                  right_on='ecom_items_id')
        #t = merge(t,
        #          DataFrame(self.get_data('thumbs')),
        #          how='left',
        #          left_on='id', # from ecom_items_ref
        #          suffixes=('', '_thumbs'),
        #          right_on='ecom_items_ref_id')

        #t = t[:500] # for debug
        return t

    def get_mapping_products(self):
        return {
            'name': self.TABLE_PRODUCT,
            'table': self.table_product,
            'dependencies' : [self.TABLE_PRODUCT_CATEGORY],
            'models':[
                {'model':'product.category',
                 'fields': {
                     'id': xml_id(self.TABLE_PRODUCT + '_brand', 'Brand'),
                     'name': 'Brand',
                 }
                },

                {'model' : 'product.product',
                 'split' : 1000,
                 'fields': {
                     'id': xml_id(self.TABLE_PRODUCT, 'ID'),
                     'categ_id/id': xml_id(self.TABLE_PRODUCT + '_brand', 'Brand'),
                     'name': 'Label',
                     'website_published': 'published',
                     'default_code': 'ID',

                     'standard_price': 'price_purchase',
                     'lst_price': 'price_sales',
                     'active': lambda record: not int(record['disabled']),

                     'public_categ_id/id': xml_id(self.TABLE_PRODUCT_CATEGORY, 'ecom_category_id'),
                     'image_medium': image('id'),
                     'description': ppconcat(
                         'color',
                         'weight',
                         'size',
                         'custom_code',
                         #'price_purchase',
                         'vat_code',
                         #'price_sales',
                         'stock_min',
                         'stock_max',
                         'packaging',
                         'packaging_pro',
                         'packaging_public',
                         'tags',
                         'eco_tax',
                         'EAN_code',
                         'disabled',
                         'body'
                     ),
                 },
             }
            ]
        }
