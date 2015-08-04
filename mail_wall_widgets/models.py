from openerp.osv import osv,fields as old_fields
from openerp import api, models, fields, tools
from openerp.tools.safe_eval import safe_eval
try:
    from openerp.addons.email_template.email_template import mako_template_env
except ImportError:
    try:
        from openerp.addons.mail.mail_template import mako_template_env
    except ImportError:
        pass

import copy
from openerp.tools.translate import _
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class mail_wall_widgets_widget(models.Model):
    _name = 'mail.wall.widgets.widget'
    _order = "sequence, id"

    _columns = {
        'name': old_fields.char('Name', required=True, translate=True),
        'type': old_fields.selection(string='Type', selection=[
            ('list', 'List'),
            ('funnel', 'Funnel'),
            ('slice', 'Slice'),
            #('', ''),
            #('', ''),
            #('', ''),
            #('', ''),
        ], help='''
Slice - use "domain" for total and "won_domain" for target
        '''),
        'description': old_fields.text('Description', translate=True),
        'group_ids': old_fields.many2many('res.groups', relation='mail_wall_widgets_widget_group', column1='widget_id', column2='group_id', string='Groups', help="User groups to show widget"),
        'model_id': old_fields.many2one('ir.model', string='Model', help='The model object for the field to evaluate'),
        'domain': old_fields.char("Filter Domain", help="Domain for filtering records. General rule, not user depending, e.g. [('state', '=', 'done')]. The expression can contain reference to 'user' which is a browse record of the current user if not in batch mode.", required=True),
        'limit': old_fields.integer('Limit', help='Limit count of records to show'),
        'order': old_fields.char('Order', help='Order of records to show'),
        'value_field_id': old_fields.many2one('ir.model.fields',
            string='Value field',
            help='The field containing the value of record'),
        'stage_field_id': old_fields.many2one('ir.model.fields',
            string='Stage field',
            help='Field to split records in funnel. It can be selection type or many2one (the later should have "sequence" field)'),
        #'stage_field_domain': old_fields.many2one('ir.model.fields',
        #    string='Stage field domain',
        #    help='(for many2one stage_field_id) Domain to find stage objects'),
        'won_domain': old_fields.char('Won domain',
            help='Domain to find won objects'),
        'field_date_id': old_fields.many2one('ir.model.fields',
            string='Date Field',
            help='The date to use for the time period evaluated'),
        'start_date': old_fields.date('Start Date'),
        'end_date': old_fields.date('End Date'),  # no start and end = always active
        'content': old_fields.char('Line template', help='Mako template to show content'),
        'value_field_monetary': old_fields.boolean('Value is monetary'),
        'cache': old_fields.boolean('Cache'),
        'active': old_fields.boolean('Active'),
        'sequence': old_fields.integer('Sequence', help='Sequence number for ordering'),
    }
    precision = fields.Float('Precision', help='round(Value/precision) * precision.  E.g. 12345,333333 will be rounded to 12345,33 for precision=0.01, and to 12000 for precision=1000', default=0.01)
    agenda = fields.Boolean('Agenda', help='Split records by date: overdue, today, tomorrow, later')
    _defaults = {
        'active': True,
        'cache': False,
        'limit': None,
        'order': None,
    }

    @api.one
    def get_data(self, user):

        domain = safe_eval(self.domain, {'user': user})
        won_domain = safe_eval(self.won_domain or '[]', {'user': user})

        field_date_name = self.field_date_id and self.field_date_id.name
        if self.start_date and field_date_name:
            domain.append((field_date_name, '>=', self.start_date))
        if self.end_date and field_date_name:
            domain.append((field_date_name, '<=', self.end_date))

        res = {
            'name': self.name,
            'type': self.type,
            'model': self.model_id.model,
            'domain': str(domain),
            'precision': self.precision,
        }
        obj = self.env[self.model_id.model]
        if self.type == 'list':
            total_count = obj.search_count(domain)
            groups = [{'test': lambda r: True}]
            if self.agenda:
                today = date.today()
                tomorrow = today + timedelta(days=1)
                def r2date(r):
                    d = getattr(r, field_date_name)
                    if d:
                        d = datetime.strptime(d, self.field_date_id.ttype=='date' and DEFAULT_SERVER_DATE_FORMAT or DEFAULT_SERVER_DATETIME_FORMAT)
                        d = d.date()
                    else:
                        d = date.today()
                    return d
                groups = [
                    {
                        'label': _('Overdue'),
                        'class': 'overdue',
                        'test': lambda r: r2date(r) < today,
                        'mandatory': False,
                    },
                    {
                        'label': _('Today'),
                        'class': 'today',
                        'test': lambda r: r2date(r) == today,
                        'mandatory': True,
                    },
                    {
                        'label': _('Tomorrow'),
                        'class': 'tomorrow',
                        'test': lambda r: r2date(r) == tomorrow,
                        'mandatory': False,
                    },
                    {
                        'label': _('Later'),
                        'class': 'later',
                        'test': lambda r: r2date(r) > tomorrow,
                        'mandatory': False,
                    },
                ]
            for g in groups:
                g['lines'] = []

            res.update({
                'more': self.limit and self.limit < total_count,
                'total_count': total_count,
                'agenda': self.agenda,
                'groups': groups,
            })
            for r in obj.search(domain, limit=self.limit, order=self.order):
                mako = mako_template_env.from_string(tools.ustr(self.content))
                content = mako.render({'record':r})
                r_json = {
                    'id': r.id,
                    #'fields': dict( (f,getattr(r,f)) for f in fields),
                    'display_mode': 'progress',
                    'state': 'inprogress',
                    'completeness': 0,
                    'name': content,
                    'description': '',
                }
                if self.value_field_id:
                    r_json['current'] = getattr(r, self.value_field_id.name)
                    if self.value_field_monetary:
                        r_json['monetary'] = 1
                for g in groups:
                    if g['test'](r):
                        g['lines'].append(r_json)
                        break
            for g in groups:
                del g['test']
        elif self.type == 'funnel':
            stage_ids = [] # [key]
            for group in obj.read_group(domain, [], [self.stage_field_id.name]):
                key = group[self.stage_field_id.name]
                if isinstance(key, (list, tuple)):
                    key = key[0]
                stage_ids.append(key)

            stages = [] # [{'name':Name, 'id': key}]
            if self.stage_field_id.ttype == 'selection':
                d = dict (self.stage_field_id.selection)
                stages = [ {'id':id, 'name':d[id]} for id in stage_ids ]
            else: # many2one
                stage_model = self.stage_field_id.relation
                for r in self.env[stage_model].browse(stage_ids):
                    stages.append({'id': r.id, 'name':r.name_get()[0][1]})

            value_field_name = self.value_field_id.name
            for stage in stages:
                d = copy.copy(domain)
                d.append( (self.stage_field_id.name, '=', stage['id']) )
                result = obj.read_group(d, [value_field_name], [])
                stage['closed_value'] = result and result[0][value_field_name] or 0.0
                stage['domain'] = str(d)

            # won value
            d = domain + won_domain
            result = obj.read_group(domain, [value_field_name], [])
            won = {'name': _('Won'),
                   'id':'__won__',
                   'closed_value': result and result[0][value_field_name] or 0.0
                   }
            stages.append(won)
            cur = 0
            for stage in reversed(stages):
                cur += stage['closed_value']
                stage['abs_value'] = cur
            total_value = stages[0]['abs_value']
            precision = self.precision
            for s in stages:
                s['rel_value'] = round(100*s['abs_value']/total_value/precision)*precision if total_value else 100
                # dummy fields
                s['display_mode'] = 'progress'
                s['monetary'] = 1

            res['stages'] = stages
            res['won'] = won
            res['conversion_rate'] = stages[-1]['rel_value']
        elif self.type == 'slice':
            value_field_name = self.value_field_id.name
            for f,d  in [('total', domain), ('won', won_domain)]:
                result = obj.read_group(d, [value_field_name], [])
                res[f] = result and result[0][value_field_name] or 0.0

            res['domain'] = str(domain)
            res['won_domain'] = str(won_domain)

            precision = self.precision
            total_value = res['total']
            res['slice'] = round(100*res['won']/res['total']/precision)*precision if res['total'] else 100
            # dummy fields
            res['display_mode'] = 'progress'
            res['monetary'] = self.value_field_monetary
        return res

class mail_wall_widgets_cache(models.Model):
    _name = 'mail.wall.widgets.cache'

    cache = fields.Text('Cached data')
    res_id = fields.Integer('Resource ID')
    res_model = fields.Integer('Resource Model')
    user_id = fields.Many2one('res.users')

class res_users(models.Model):
    _inherit = 'res.users'

    @api.v7
    def get_serialised_mail_wall_widgets_summary(self, cr, uid, excluded_categories=None, context=None):
        return self._get_serialised_mail_wall_widgets_summary(cr, uid, uid, excluded_categories=excluded_categories, context=context)[0]

    @api.one
    def _get_serialised_mail_wall_widgets_summary(self, excluded_categories=None):
        """
        [
            {
                'id': ...,
                'model': ...,
                'currency': <res.currency id>,
                'data': (depend on model)
            },
        ]
        """
        user = self.env.user
        res = []
        model = 'mail.wall.widgets.widget'
        domain = [('group_ids', 'in', user.groups_id.ids), ('active', '=', True)]
        for widget in self.env[model].search(domain, order='sequence'):
            if widget.cache:
                #TODO
                continue
            res.append({
                'model': model,
                'id': widget.id,
                'currency': user.company_id.currency_id.id,
                'data': widget.get_data(user)[0],
            })
        return res

    #def get_challenge_suggestions(self, cr, uid, context=None):
    #    """Return the list of challenges suggested to the user"""
    #    challenge_info = []
    #    challenge_obj = self.pool.get('mail_wall_widgets.challenge')
    #    challenge_ids = challenge_obj.search(cr, uid, [('invited_user_ids', 'in', uid), ('state', '=', 'inprogress')], context=context)
    #    for challenge in challenge_obj.browse(cr, uid, challenge_ids, context=context):
    #        values = {
    #            'id': challenge.id,
    #            'name': challenge.name,
    #            'description': challenge.description,
    #        }
    #        challenge_info.append(values)
    #    return challenge_info
