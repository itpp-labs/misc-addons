# -*- coding: utf-8 -*-
import dateutil
import pytz
import babel.dates

from openerp import models, api


class GroupByExtra(models.AbstractModel):
    _name = "base_groupby_extra"

    @api.model
    def _read_group_process_groupby(self, gb, query):
        split = gb.split(':')
        field_type = self._fields[split[0]].type
        gb_function = split[1] if len(split) == 2 else None
        temporal = field_type in ('date', 'datetime')
        tz_convert = field_type == 'datetime' and self._context.get('tz') in pytz.all_timezones
        qualified_field = self._inherits_join_calc(self._table, split[0], query)

        if temporal and gb_function in ['hour']:
            # BEGIN New stuff
            display_formats = {
                'hour': 'hh:00 dd MMM',
            }
            time_intervals = {
                'hour': dateutil.relativedelta.relativedelta(hours=1),
            }
            # END New stuff
            if tz_convert:
                qualified_field = "timezone('%s', timezone('UTC',%s))" % (self._context.get('tz', 'UTC'), qualified_field)
            qualified_field = "date_trunc('%s', %s)" % (gb_function or 'month', qualified_field)
            res = {
                'field': split[0],
                'groupby': gb,
                'type': field_type,
                'display_format': display_formats[gb_function or 'month'] if temporal else None,
                'interval': time_intervals[gb_function or 'month'] if temporal else None,
                'tz_convert': tz_convert,
                'qualified_field': qualified_field
            }
        else:
            res = super(GroupByExtra, self)._read_group_process_groupby(gb, query)
        return res

    # 9.0 only
    def _read_group_format_result(self, data, annotated_groupbys, groupby, groupby_dict, domain, context):
        """
        Modify built-in function to call format_datetime (original
        implementation calls only format_date)
        """
        domain_group = [dom for gb in annotated_groupbys for dom in self._read_group_get_domain(gb, data[gb['groupby']])]
        for k, v in data.iteritems():
            gb = groupby_dict.get(k)
            if gb and gb['type'] in ('datetime') and v:
                data[k] = babel.dates.format_datetime(v, format=gb['display_format'], locale=context.get('lang', 'en_US'))
            elif gb and gb['type'] in ('date') and v:
                data[k] = babel.dates.format_date(v, format=gb['display_format'], locale=context.get('lang', 'en_US'))

        data['__domain'] = domain_group + domain
        if len(groupby) - len(annotated_groupbys) >= 1:
            data['__context'] = {'group_by': groupby[len(annotated_groupbys):]}
        del data['id']
        return data
