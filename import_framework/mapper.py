# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import tools
import re
import math


class Mapper(object):

    """
        super class for all mapper class
        They are call before import data
        to transform the mapping into real value that we
        will import

        the call function receive a dictionary with external data
            'external_field' : value
    """

    def __call__(self, external_values):
        raise NotImplementedError()


class Dbmapper(Mapper):

    """
        Super class for mapper that need to access to
        data base or any function of the import_framework

        self.parent contains a reference to the instance of
        the import framework
    """

    def set_parent(self, parent):
        self.parent = parent

    def res2xmlid(self, model, res_id):
        data = self.parent.pool['ir.model.data'].search(self.parent.cr,
                                                        self.parent.uid,
                                                        [('res_id', '=', res_id),
                                                            ('model', '=', model),
                                                         ])

        if not data:
            return []
        return self.parent.pool['ir.model.data'].browse(self.parent.cr, self.parent.uid, data)


class Concat(Mapper):

    """
        Use : contact('field_name1', 'field_name2', delimiter='_')
        concat value of fields using the delimiter, delimiter is optional
        and by default is a space
    """

    def __init__(self, *arg, **delimiter):
        self.arg = arg
        self.delimiter = delimiter and delimiter.get('delimiter', ' ') or ' '

    def __call__(self, external_values):
        return self.delimiter.join(map(lambda x: tools.ustr(external_values.get(x, '')or ''), self.arg))


class TagsFromFields(Dbmapper):

    def __init__(self, table, field_list):
        self.table = table
        self.field_list = field_list

    def __call__(self, external_values):
        res = []
        for f in self.field_list:
            value = external_values.get(f)
            value = value or ''
            if not isinstance(value, basestring):
                value = str(value)
            for v in value.split(','):
                v = do_clean_sugar(v)
                v = do_clean_xml_id(v)
                if v:
                    id = self.parent._generate_xml_id(v, self.table + f)
                    res.append(id)
        return ','.join(res)


class Ppconcat(Mapper):

    """
        Use : contact('field_name1', 'field_name2', delimiter='_')
        concat external field name and value of fields using the delimiter,
        delimiter is optional and by default is a two line feeds

    """

    def __init__(self, *arg, **kwargs):
        self.arg = arg
        self.delimiter = kwargs and kwargs.get('delimiter', ' ') or '\n\n'
        self.skip_value = kwargs and kwargs.get('skip_value')
        if not isinstance(self.skip_value, str):
            self.skip_value = '^^'

    def __call__(self, external_values):
        return self.delimiter.join(map(lambda x: x + ": " + tools.ustr(external_values.get(x, '')), filter(lambda x: external_values.get(x) and (self.skip_value != external_values.get(x)), self.arg)))


class First(Mapper):

    def __init__(self, *arg, **kwargs):
        self.arg = arg
        self.lower = kwargs and kwargs.get('lower') or False

    def __call__(self, external_values):
        v = ''
        for a in self.arg:
            v = external_values.get(a, '')
            if v:
                break
        if v and self.lower:
            v = v.lower()
        return v


class Fixdate(Mapper):

    """
    convert '2010-02-12 13:26:25' to '2010-02-12'
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, external_values):
        s = external_values.get(self.field_name)
        if not s:
            return ''
        return str(s).split(' ')[0]


class Const(Mapper):

    """
        Use : const(arg)
        return always arg
    """

    def __init__(self, val):
        self.val = val

    def __call__(self, external_values):
        return self.val


def do_clean_xml_id(value):
    return re.sub('[\'", ^]', '_', (value and unicode(value) or ''))


class Value(Mapper):

    """
        Use : value(external_field_name)
        Return the value of the external field name
        this is equivalent to the a single string

        usefull for call if you want your call get the value
        and don't care about the name of the field
        call(self.method, value('field1'))
    """

    def __init__(self, val, default='', fallback=False, lower=False):
        self.val = val
        self.default = default
        self.fallback = fallback
        self.lower = lower

    def __call__(self, external_values):
        val = external_values.get(self.val)
        if self.fallback and not val:
            val = external_values.get(self.fallback)
        val = val or self.default
        if self.lower:
            val = (str(val) or '').lower()
        return val


class MapperInt(Mapper):

    def __init__(self, val, default=0):
        self.val = val
        self.default = default

    def __call__(self, external_values):
        val = external_values.get(self.val, self.default)
        return val and int(val) or 0


def do_clean_sugar(v):
    return (v or '').replace('^', '').strip()


class CleanSugar(Mapper):

    def __init__(self, val, default=0):
        self.val = val
        self.default = default

    def __call__(self, external_values):
        val = external_values.get(self.val, self.default)
        return do_clean_sugar(val)


class MapVal(Mapper):

    """
        Use : map_val(external_field, val_mapping)
        where val_mapping is a dictionary
        with external_val : openerp_val

        usefull for selection field like state
        to map value
    """

    def __init__(self, val, map, default=''):
        self.val = Value(val)
        self.map = map
        self.default = default

    def __call__(self, external_values):
        return self.map.get(self.val(external_values), self.default)


class Ref(Dbmapper):

    """
        Use : ref(table_name, external_id)
        return the xml_id of the ressource

        to associate an already imported object with the current object
    """

    def __init__(self, table, field_name):
        self.table = table
        self.field_name = field_name

    def __call__(self, external_values):
        return self.parent.xml_id_exist(self.table, external_values.get(self.field_name))


class Refbyname(Dbmapper):

    """
        Use : refbyname(table_name, external_name, res.model)
        same as ref but use the name of the ressource to find it
    """

    def __init__(self, table, field_name, model):
        self.table = table
        self.field_name = field_name
        self.model = model

    def __call__(self, external_values):
        v = external_values.get(self.field_name, '')
        return self.parent.name_exist(self.table, v, self.model)


class XmlId(Dbmapper):

    def __init__(self, table, field_name='id'):
        self.table = table
        self.field_name = field_name

    def __call__(self, external_values):
        field_value = external_values.get(self.field_name)
        if isinstance(field_value, float) and math.isnan(field_value):
            return ''
        field_value = do_clean_xml_id(field_value)
        if not field_value:
            return ''
        return self.parent._generate_xml_id(field_value, self.table)


class User2partner(Dbmapper):

    def __init__(self, table_user, field_name='id'):
        self.table_user = table_user
        # self.table_partner = table_partner
        self.field_name = field_name

    def __call__(self, external_values):
        id = XmlId(self.table_user, self.field_name)
        id.set_parent(self.parent)
        user_xml_id = id(external_values)
        return user_xml_id + '_res_partner'


class UserByLogin(Dbmapper):

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, external_values):
        login = external_values.get(self.field_name)
        if not login:
            return ''
        id = self.parent.pool['res.users'].search(self.parent.cr, self.parent.uid, [('login', '=', login)], context=self.parent.context)
        if id:
            return id[0]
        else:
            return ''


FIX_COUNTRY = {
    'UK': 'United Kingdom'
}


class CountryByName(Dbmapper):

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, external_values):
        value = external_values.get(self.field_name)
        if not value:
            return ''
        value = FIX_COUNTRY.get(value, value)
        id = self.parent.pool['res.country'].search(self.parent.cr, self.parent.uid,
                                                    [('name', '=', value)], context=self.parent.context)
        if id:
            return id[0]
        else:
            return ''


class ResId(Dbmapper):

    def __init__(self, get_table, field_name, default='0'):
        self.get_table = get_table
        self.field_name = field_name
        self.default = default

    def __call__(self, external_values):
        id = XmlId(self.get_table(external_values), self.field_name)
        id.set_parent(self.parent)
        xmlid = id(external_values)
        res_id = self.parent.pool['ir.model.data'].xmlid_to_res_id(self.parent.cr,
                                                                   self.parent.uid,
                                                                   '.' + xmlid)
        return res_id and str(res_id) or self.default


class Emails2partners(Dbmapper):

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, external_values):
        alias_domain = self.parent.cache.get('alias_domain', None)
        if alias_domain is None:
            ir_config_parameter = self.parent.pool.get("ir.config_parameter")
            alias_domain = ir_config_parameter.get_param(self.parent.cr, self.parent.uid, "mail.catchall.domain")

            alias_domain = alias_domain or ''
            self.parent.cache['alias_domain'] = alias_domain

        s = external_values.get(self.field_name, '')
        s = s.lower()
        res = []
        for email in re.findall('[^<>, ]*@[^<>, ]*', s):
            if alias_domain and alias_domain == email.split('@')[1]:
                res_users = self.parent.pool.get("res.users")
                user_id = res_users.search(self.parent.cr, self.parent.uid,
                                           [('alias_name', '=', email.split('@')[0])])
                if user_id:
                    user_id = user_id[0]
                    partner_id = res_users.browse(self.parent.cr, self.parent.uid,
                                                  user_id).partner_id.id
                    # tmp
                    res.append(str(partner_id))
                    continue
                else:

                    pass

            #
            partner_id = self.parent.pool['res.partner'].search(self.parent.cr,
                                                                self.parent.uid,
                                                                [('email', '=', email),
                                                                 ])

            if partner_id:
                partner_id = partner_id[0]

                # tmp
                res.append(str(partner_id))
                continue
            else:

                pass

        res = ','.join(res)

        return res


class Call(Mapper):

    """
        Use : call(function, arg1, arg2)
        to call the function with external val follow by the arg specified
    """

    def __init__(self, fun, *arg):
        self.fun = fun
        self.arg = arg

    def __call__(self, external_values):
        args = []
        for arg in self.arg:
            if isinstance(arg, Mapper):
                args.append(arg(external_values))
            else:
                args.append(arg)
        return self.fun(external_values, *args)
