# -*- coding: utf-8 -*-
from . import mapper
try:
    from pandas import DataFrame
except ImportError:
    pass
import logging
_logger = logging.getLogger(__name__)


class CreateChilds(object):

    def __init__(self, childs):

        # extend childs to same set of fields

        # collect fields
        fields = set()
        for c in childs:
            for f in c:
                fields.add(f)

        # extend childs
        for c in childs:
            for f in fields:
                if f not in c:
                    c[f] = mapper.const('')

        self.childs = childs

    def get_childs(self):
        return self.childs


class ImportBase(object):

    def __init__(self, pool, cr, uid,
                 instance_name,
                 module_name,
                 email_to_notify=False,
                 import_dir='/tmp/',  # path to save *.csv files for debug or manual upload
                 run_import=True,
                 context=None):
        # Thread.__init__(self)
        self.import_options = {'quoting': '"', 'separator': ',', 'headers': True}
        self.external_id_field = 'id'
        self.pool = pool
        self.cr = cr
        self.uid = uid
        self.instance_name = instance_name
        self.module_name = module_name
        self.context = context or {}
        self.email = email_to_notify
        self.table_list = []
        # self.logger = logging.getLogger(module_name)
        self.cache = {}
        self.import_dir = import_dir
        self.run_import = run_import
        self.import_num = 1
        self.initialize()

    def initialize(self):
        """
            init before import
            usually for the login
        """

    def finalize(self):
        """
            init after import
        """

    def init_run(self):
        """
            call after intialize run in the thread, not in the main process
            TO use for long initialization operation
        """

    def get_data(self, table):
        """
            @return: a list of dictionaries
                each dictionnaries contains the list of pair  external_field_name : value
        """
        return [{}]

    def get_link(self, from_table, ids, to_table):
        """
            @return: a dictionaries that contains the association between the id (from_table)
                     and the list (to table) of id linked
        """
        return {}

    def get_external_id(self, data):
        """
            @return the external id
                the default implementation return self.external_id_field (that has 'id') by default
                if the name of id field is different, you can overwrite this method or change the value
                of self.external_id_field
        """
        return data[self.external_id_field]

    def get_mapping(self):
        """
            @return: { TABLE_NAME : {
                'model' : 'openerp.model.name',
                # if true import the table if not just resolve dependencies, use for meta package, by default => True
                # Not required
                'import' : True or False,
                # Not required
                'dependencies' : [TABLE_1, TABLE_2],
                # Not required
                'hook' : self.function_name, # get the val dict of the object, return the same val dict or False
                'map' : { @see mapper
                    'openerp_field_name' : 'external_field_name', or val('external_field_name')
                    'openerp_field_id/id' : ref(TABLE_1, 'external_id_field'), # make the mapping between the external id and the xml on the right
                    'openerp_field2_id/id_parent' : ref(TABLE_1,'external_id_field') # indicate a self dependencies on openerp_field2_id
                    'state' : map_val('state_equivalent_field', mapping), # use get_state_map to make the mapping between the value of the field and the value of the state
                    'text_field' : concat('field_1', 'field_2', .., delimiter=':'), # concat the value of the list of field in one
                    'description_field' : ppconcat('field_1', 'field_2', .., delimiter='\n\t'), # same as above but with a prettier formatting
                    'field' : call(callable, arg1, arg2, ..), # call the function with all the value, the function should send the value : self.callable
                    'field' : callable
                    'field' : call(method, val('external_field') interface of method is self, val where val is the value of the field
                    'field' : const(value) # always set this field to value
                    + any custom mapper that you will define
                }
            },

            }
        """
        return {}

    def default_hook(self, val):
        """
            this hook will be apply on each table that don't have hook
            here we define the identity hook
        """
        return val

    def hook_ignore_all(self, *args):
        # for debug
        return None

    def get_hook_ignore_empty(self, *args):
        def f(external_values):
            ignore = True
            for key in args:
                v = (external_values.get(key) or '').strip()
                if v:
                    ignore = False
                    break
            if ignore:
                return None
            else:
                return external_values
        return f

    def prepare_mapping(self, mapping):
        res = {}
        for m in mapping:
            res[m['name']] = m
        return res

    def run(self):
        self.mapped = set()
        self.mapping = self.prepare_mapping(self.get_mapping())
        self.resolve_dependencies([k for k in self.mapping])
        _logger.info('finalize...')
        self.finalize()
        _logger.info('finalize done')

    def _fix_size_limit(self):
        import sys
        import csv
        maxInt = sys.maxsize
        decrement = True

        while decrement:
            # decrease the maxInt value by factor 10
            # as long as the OverflowError occurs.

            decrement = False
            try:
                csv.field_size_limit(maxInt)
            except OverflowError:
                maxInt = int(maxInt / 10)
                decrement = True

    def do_import(self, import_list, context):
        self._fix_size_limit()
        # import
        import_obj = self.pool['base_import.import']
        for imp in import_list:
            try:
                messages = import_obj.do(self.cr, self.uid,
                                         imp.get('id'), imp.get('fields'),
                                         self.import_options, context=context)
                _logger.info('import_result:\n%s' % messages)
            except Exception:

                import traceback
                import StringIO
                sh = StringIO.StringIO()
                traceback.print_exc(file=sh)
                error = sh.getvalue()

                error = "Error during import\n%s\n%s" % (imp, error)
                _logger.error(error)

                raise Exception(error)
            self.cr.commit()

    def resolve_dependencies(self, deps):
        for dname in deps:
            if dname in self.mapped:
                continue
            self.mapped.add(dname)
            mtable = self.mapping.get(dname)
            if not mtable:
                _logger.error('no mapping found for %s' % dname)
                continue
            self.resolve_dependencies(mtable.get('dependencies', []))
            self.map_and_import(mtable)

    def map_and_import(self, mtable):
        _logger.info('read table %s' % mtable.get('name'))
        records = mtable.get('table')()

        for mmodel in mtable.get('models'):
            split = mmodel.get('split')
            if not split:
                _logger.info('map and import: import-%s' % self.import_num)
                self.map_and_import_batch(mmodel, records)
            else:
                i = 0
                while True:
                    _logger.info('importing batch # %s (import-%s)' % (i, self.import_num))
                    rr = records[i * split:(i + 1) * split]
                    if len(rr):
                        self.map_and_import_batch(mmodel, rr)
                        i += 1
                    else:
                        break
            finalize = mmodel.get('finalize')
            if finalize:
                _logger.info('finalize model...')
                finalize()
                _logger.info('finalize model done')

    def map_and_import_batch(self, mmodel, records):
        import_list = self.do_mapping(records, mmodel)
        context = mmodel.get('context')
        if context:
            context = context()
        self.do_import(import_list, context)

    def do_mapping(self, records, mmodel):

        hook = mmodel.get('hook', self.default_hook)

        res = []

        mfields = self._preprocess_mapping(mmodel.get('fields'))
        _logger.info('mapping records to %s: %s' % (mmodel.get('model'), len(records)))
        for key, r in records.iterrows():
            hooked = hook(dict(r))
            if not isinstance(hooked, list):
                hooked = [hooked]

            for dict_sugar in hooked:
                if dict_sugar:
                    fields, values_list = self._fields_mapp(dict_sugar, mfields)
                    res.extend(values_list)

        if not res:
            _logger.info("no records to import")
            return []
        res = DataFrame(res)
        data_binary = res.to_csv(sep=self.import_options.get('separator'),
                                 quotechar=self.import_options.get('quoting'),
                                 index=False,
                                 header=fields,
                                 encoding='utf-8'
                                 )

        if self.import_dir:
            file_name = '%s/import-%03d-%s.csv' % (
                self.import_dir,
                self.import_num,
                mmodel.get('model'),
            )
            with open(file_name, 'w') as f:
                f.write(data_binary)

            self.import_num += 1

        if not self.run_import:
            return []
        id = self.pool['base_import.import'].create(self.cr, self.uid,
                                                    {'res_model': mmodel.get('model'),
                                                     'file': data_binary,
                                                     'file_name': mmodel.get('model'),
                                                     })
        return [{'id': id, 'fields': fields}]

    def _preprocess_mapping(self, mapping):
        """
            Preprocess the mapping :
            after the preprocces, everything is
            callable in the val of the dictionary

            use to allow syntaxical sugar like 'field': 'external_field'
            instead of 'field' : value('external_field')
        """
        # m = dict(mapping)
        m = mapping
        for key, value in m.items():
            if isinstance(value, basestring):
                m[key] = mapper.value(value)
            # set parent for instance of dbmapper
            elif isinstance(value, mapper.dbmapper):
                value.set_parent(self)
            elif isinstance(value, CreateChilds):
                # {'child_ids':[{'id':id1, 'name':name1}, {'id':id2, 'name':name2}]}
                # ->
                # {'child_ids/id':[id1, id2], 'child_ids/name': [name1, name2]}
                for c in value.get_childs():
                    self._preprocess_mapping(c)
                    for ckey, cvalue in c.items():
                        new_key = '%s/%s' % (key, ckey)
                        if new_key not in m:
                            m[new_key] = []
                        m[new_key].append(cvalue)
                del m[key]  # delete 'child_ids'
        return m

    def _fields_mapp(self, dict_sugar, openerp_dict):
        """
{'name': name0, 'child_ids/id':[id1, id2], 'child_ids/name': [name1, name2]} ->

fields =
['name', 'child_ids/id', 'child_ids/name']
res = [
[name0, '',''], # i=-1
['', id1, name1] # i=0
['', id2, name2] # i=1
]
        """
        res = []
        i = -1
        while True:
            fields = []
            data_lst = []
            for key, val in openerp_dict.items():
                if key not in fields:
                    fields.append(key)
                    if isinstance(val, list) and len(val) > i and i >= 0:
                        value = val[i](dict_sugar)
                    elif not isinstance(val, list) and i == -1:
                        value = val(dict_sugar)
                    else:
                        value = ''
                    data_lst.append(value)
            if any(data_lst):
                add = True
                if i >= 0:
                    add = False
                    # ignore empty lines
                    for pos, val in enumerate(data_lst):
                        if fields[pos].endswith('/id'):
                            continue
                        if val:
                            add = True
                            break
                if add:
                    res.append(data_lst)
                i += 1
            else:
                break
        return fields, res

    def xml_id_exist(self, table, external_id):
        """
            Check if the external id exist in the openerp database
            in order to check if the id exist the table where it come from
            should be provide
            @return the xml_id generated if the external_id exist in the database or false
        """
        if not external_id:
            return False

        xml_id = self._generate_xml_id(external_id, table)
        id = self.pool.get('ir.model.data').search(self.cr, self.uid, [('name', '=', xml_id), ('module', '=', self.module_name)])
        return id and xml_id or False

    def _generate_xml_id(self, name, table):
        """
            @param name: name of the object, has to be unique in for a given table
            @param table : table where the record we want generate come from
            @return: a unique xml id for record, the xml_id will be the same given the same table and same name
                     To be used to avoid duplication of data that don't have ids
        """
        sugar_instance = self.instance_name
        name = name.replace('.', '_').replace(',', '_')
        return sugar_instance + "_" + table + "_" + name
