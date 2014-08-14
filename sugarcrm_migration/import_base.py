import logging
import mapper
from pandas import DataFrame
import logging
_logger = logging.getLogger(__name__)

class import_base(object):

    def __init__(self, pool, cr, uid,
                 instance_name,
                 module_name,
                 email_to_notify=False,
                 context=None):
        #Thread.__init__(self)
        self.import_options = {'quoting':'"', 'separator':',', 'headers':True}
        self.external_id_field = 'id'
        self.pool = pool
        self.cr = cr
        self.uid = uid
        self.instance_name = instance_name
        self.module_name = module_name
        self.context = context or {}
        self.email = email_to_notify
        self.table_list = []
        #self.logger = logging.getLogger(module_name)
        self.cache = {}
        self.initialize()


    def initialize(self):
        """
            init before import
            usually for the login
        """
        pass

    def init_run(self):
        """
            call after intialize run in the thread, not in the main process
            TO use for long initialization operation
        """
        pass

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
                #if true import the table if not just resolve dependencies, use for meta package, by default => True
                #Not required
                'import' : True or False,
                #Not required
                'dependencies' : [TABLE_1, TABLE_2],
                #Not required
                'hook' : self.function_name, #get the val dict of the object, return the same val dict or False
                'map' : { @see mapper
                    'openerp_field_name' : 'external_field_name', or val('external_field_name')
                    'openerp_field_id/id' : ref(TABLE_1, 'external_id_field'), #make the mapping between the external id and the xml on the right
                    'openerp_field2_id/id_parent' : ref(TABLE_1,'external_id_field') #indicate a self dependencies on openerp_field2_id
                    'state' : map_val('state_equivalent_field', mapping), # use get_state_map to make the mapping between the value of the field and the value of the state
                    'text_field' : concat('field_1', 'field_2', .., delimiter=':'), #concat the value of the list of field in one
                    'description_field' : ppconcat('field_1', 'field_2', .., delimiter='\n\t'), #same as above but with a prettier formatting
                    'field' : call(callable, arg1, arg2, ..), #call the function with all the value, the function should send the value : self.callable
                    'field' : callable
                    'field' : call(method, val('external_field') interface of method is self, val where val is the value of the field
                    'field' : const(value) #always set this field to value
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

    def prepare_mapping(self, mapping):
        res = {}
        for m in mapping:
            res[m['name']] = m
        return res

    def run(self):
        self.mapped = set()
        self.mapping = self.prepare_mapping(self.get_mapping())
        self.resolve_dependencies([k for k in self.mapping])

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
                maxInt = int(maxInt/10)
                decrement = True

    def do_import(self, import_list):
        self._fix_size_limit()
        # import
        import_obj = self.pool['base_import.import']
        for imp in import_list:
            try:
                messages = import_obj.do(self.cr, self.uid,
                                         imp.get('id'), imp.get('fields'),
                                         self.import_options)
                _logger.info('import_result:\n%s'%messages)
            except Exception as e:

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
        import_list = []
        for dname in deps:
            if dname in self.mapped:
                continue
            self.mapped.add(dname)
            m = self.mapping.get(dname)
            if not m:
                #continue # only for debug!
                pass
            self.resolve_dependencies(m.get('dependencies', []))
            import_list = self.map_data(m)
            self.do_import(import_list)

    def map_data(self, m):
        _logger.info('read table %s' % m.get('name'))
        records = m.get('table')()
        hook = m.get('hook', self.default_hook)

        res = []

        map_fields = self._preprocess_mapping(m.get('map'))
        _logger.info('mapping records of %s: %s' %( m.get('name'), len(records)))
        for key, r in records.iterrows():
            dict_sugar = dict(r)
            dict_sugar = hook(dict_sugar)
            if dict_sugar:
                fields, values = self._fields_mapp(dict_sugar, map_fields)
                res.append(values)
            else:
                #print 'skipped after hook', dict(r)
                pass

        res = DataFrame(res)
        data_binary = res.to_csv(sep=self.import_options.get('separator'),
                                 quotechar=self.import_options.get('quoting'),
                                 index=False,
                                 encoding='utf-8'
                                 )

        id = self.pool['base_import.import'].create(self.cr, self.uid,
            {'res_model':m.get('model'),
             'file': data_binary,
             'file_name': m.get('name'),
             })
        return [{'id':id, 'fields':fields}]

    def _preprocess_mapping(self, mapping):
        """
            Preprocess the mapping :
            after the preprocces, everything is
            callable in the val of the dictionary

            use to allow syntaxical sugar like 'field': 'external_field'
            instead of 'field' : value('external_field')
        """
        map = dict(mapping)
        for key, value in map.items():
            if isinstance(value, basestring):
                map[key] = mapper.value(value)
            #set parent for instance of dbmapper
            elif isinstance(value, mapper.dbmapper):
                value.set_parent(self)
        return map

    def _fields_mapp(self,dict_sugar, openerp_dict):
        """
            call all the mapper and transform data
            to be compatible with import_data
        """
        fields=[]
        data_lst = []
        #mapping = self._preprocess_mapping(openerp_dict)
        for key,val in openerp_dict.items():
            if key not in fields:
                fields.append(key)
                value = val(dict_sugar)
                data_lst.append(value)
        return fields, data_lst

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
