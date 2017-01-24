# -*- coding: utf-8 -*-
from openerp.osv import fields as old_fields
from openerp import api, models, fields
from openerp.addons.gamification.models.challenge import start_end_date_for_period
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
from openerp import osv


class GamificationGoalDefinition(models.Model):
    _inherit = 'gamification.goal.definition'

    click_action = fields.Text('Click action', help='Executed when user click on goal. Keep empty to show records in domain.')

    _columns = {
        'computation_mode': old_fields.selection([
            ('manually', 'Recorded manually'),
            ('count', 'Automatic: number of records'),
            ('sum', 'Automatic: sum on a field'),
            ('avg', 'Automatic: avg on a field'),
            ('min', 'Automatic: min on a field'),
            ('max', 'Automatic: max on a field'),
            ('python', 'Automatic: execute a specific Python code'),
        ],
            string="Computation Mode",
            help="Defined how will be computed the goals. The result of the operation will be stored in the field 'Current'.",
            required=True),
    }


class GamificationGoal(models.Model):
    _inherit = 'gamification.goal'

    @api.v7
    def _get_sum(self, cr, uid, ids, fname, arg, context=None):
        # copy-paste from addons/gamification/models/goal.py::update

        result = {}
        for goal in self.browse(cr, uid, ids, context=context):
            definition = goal.definition_id
            if True:  # keep original indent
                obj = self.pool.get(definition.model_id.model)
                field_date_name = definition.field_date_id and definition.field_date_id.name or False
                if True:  # keep original indent
                    # for goal in goals:
                    if True:
                        # eval the domain with user replaced by goal user object
                        domain = safe_eval(definition.domain, {'user': goal.user_id})

                        # add temporal clause(s) to the domain if fields are filled on the goal
                        if goal.start_date and field_date_name:
                            domain.append((field_date_name, '>=', goal.start_date))
                        if goal.end_date and field_date_name:
                            domain.append((field_date_name, '<=', goal.end_date))

                        # if definition.computation_mode == 'sum':
                        if fname == 'sum':
                            field_name = definition.field_id.name
                            # TODO for master: group on user field in batch mode
                            res = obj.read_group(cr, uid, domain, [field_name], [], context=context)
                            new_value = res and res[0][field_name] or 0.0

                        else:  # fname == 'count'
                            new_value = obj.search(cr, uid, domain, context=context, count=True)
                        result[goal.id] = new_value
        return result

    _columns = {
        'sum': old_fields.function(_get_sum, string='Sum', type='float', help='Compute goal as sum'),
        'count': old_fields.function(_get_sum, string='Count', type='float', help='Compute goal as count'),
    }

    @api.v7
    def update(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        # commit = context.get('commit_gamification', False)

        goals_by_definition = {}
        all_goals = {}
        for goal in self.browse(cr, uid, ids, context=context):
            if goal.state in ('draft', 'canceled'):
                # draft or canceled goals should not be recomputed
                continue

            goals_by_definition.setdefault(goal.definition_id, []).append(goal)
            all_goals[goal.id] = goal

        other_ids = []
        for definition, goals in goals_by_definition.items():
            goals_to_write = dict((goal.id, {}) for goal in goals)

            if definition.computation_mode not in ('avg', 'min', 'max'):
                other_ids.extend([goal.id for goal in goals])
            else:
                obj = self.pool.get(definition.model_id.model)
                field_date_name = definition.field_date_id and definition.field_date_id.name or False

                if False:
                    # keep original indent
                    pass
                else:
                    for goal in goals:
                        # eval the domain with user replaced by goal user object
                        domain = safe_eval(definition.domain, {'user': goal.user_id})

                        # add temporal clause(s) to the domain if fields are filled on the goal
                        if goal.start_date and field_date_name:
                            domain.append((field_date_name, '>=', goal.start_date))
                        if goal.end_date and field_date_name:
                            domain.append((field_date_name, '<=', goal.end_date))

                        if definition.computation_mode == 'avg':
                            field_name = definition.field_id.name
                            # TODO for master: group on user field in batch mode
                            res = obj.read_group(cr, uid, domain, [field_name], [], context=context)
                            new_value = res and res[0][field_name] or 0.0
                            count = obj.search_count(cr, uid, domain, context=context)
                            if count != 0:
                                new_value = float(new_value) / count

                        else:  # computation_mode in ('min', 'max')
                            field_name = definition.field_id.name
                            try:
                                # works if field is stored
                                orderby = '%s %s' % (
                                    field_name,
                                    'ASC' if definition.computation_mode == 'min' else 'DESC'
                                )
                                ids = obj.search(cr, uid, domain, context=context, order=orderby, limit=1)
                                res = obj.read(cr, uid, ids, [field_name], context=context)
                                new_value = res and res[0][field_name] or 0.0
                            except ValueError:
                                ids = obj.search(cr, uid, domain, context=context)
                                res = obj.read(cr, uid, ids, [field_name], context=context)
                                res = sorted(res, key=lambda r: r[field_name], reverse=definition.computation_mode == 'max')
                                new_value = res and res[0][field_name] or 0.0

                        # avoid useless write if the new value is the same as the old one
                        if new_value != goal.current:
                            goals_to_write[goal.id]['current'] = new_value

            for goal_id, value in goals_to_write.items():
                if not value:
                    continue
                goal = all_goals[goal_id]

                # check goal target reached
                if (goal.definition_id.condition == 'higher' and value.get('current', goal.current) >= goal.target_goal) \
                        or (goal.definition_id.condition == 'lower' and value.get('current', goal.current) <= goal.target_goal):
                    value['state'] = 'reached'

                # check goal failure
                elif goal.end_date and fields.date.today() > goal.end_date:
                    value['state'] = 'failed'
                    value['closed'] = True
                if value:
                    self.write(cr, uid, [goal.id], value, context=context)
            # if commit:
            #    cr.commit()

        return super(GamificationGoal, self).update(cr, uid, other_ids, context=context)


class GamificationChallenge(models.Model):
    _inherit = 'gamification.challenge'

    show_reached = fields.Boolean('Show after reaching', defaults=False)
    precision = fields.Float('Precision', help='round(Value/precision) * precision.  E.g. 12345,333333 will be rounded to 12345,33 for precision=0.01, and to 12000 for precision=1000', default=0.01)

    @api.v7
    def _get_serialized_challenge_lines(self, cr, uid, challenge, user_id=False, restrict_goal_ids=False, restrict_top=False, context=None):
        """Return a serialised version of the goals information if the user has not completed every goal

        :challenge: browse record of challenge to compute
        :user_id: res.users id of the user retrieving progress (False if no distinction, only for ranking challenges)
        :restrict_goal_ids: <list(int)> compute only the results for this subset if gamification.goal ids, if False retrieve every goal of current running challenge
        :restrict_top: <int> for challenge lines where visibility_mode == 'ranking', retrieve only these bests results and itself, if False retrieve all
            restrict_goal_ids has priority over restrict_top

        format list
        # if visibility_mode == 'ranking'
        {
            'name': <gamification.goal.description name>,
            'description': <gamification.goal.description description>,
            'condition': <reach condition {lower,higher}>,
            'computation_mode': <target computation {manually,count,sum,python}>,
            'monetary': <{True,False}>,
            'suffix': <value suffix>,
            'action': <{True,False}>,
            'display_mode': <{progress,boolean}>,
            'target': <challenge line target>,
            'own_goal_id': <gamification.goal id where user_id == uid>,
            'goals': [
                {
                    'id': <gamification.goal id>,
                    'rank': <user ranking>,
                    'user_id': <res.users id>,
                    'name': <res.users name>,
                    'state': <gamification.goal state {draft,inprogress,reached,failed,canceled}>,
                    'completeness': <percentage>,
                    'current': <current value>,
                }
            ]
        },
        # if visibility_mode == 'personal'
        {
            'id': <gamification.goal id>,
            'name': <gamification.goal.description name>,
            'description': <gamification.goal.description description>,
            'condition': <reach condition {lower,higher}>,
            'computation_mode': <target computation {manually,count,sum,python}>,
            'monetary': <{True,False}>,
            'suffix': <value suffix>,
            'action': <{True,False}>,
            'display_mode': <{progress,boolean}>,
            'target': <challenge line target>,
            'state': <gamification.goal state {draft,inprogress,reached,failed,canceled}>,
            'completeness': <percentage>,
            'current': <current value>,
        }
        """
        goal_obj = self.pool.get('gamification.goal')
        (start_date, end_date) = start_end_date_for_period(challenge.period)

        res_lines = []
        all_reached = True
        for line in challenge.line_ids:
            line_data = {
                'name': line.definition_id.name,
                'description': line.definition_id.description,
                'condition': line.definition_id.condition,
                'computation_mode': line.definition_id.computation_mode,
                'monetary': line.definition_id.monetary,
                'suffix': line.definition_id.suffix,
                'action': True if line.definition_id.action_id else False,
                'display_mode': line.definition_id.display_mode,
                'target': line.target_goal,
            }
            domain = [
                ('line_id', '=', line.id),
                ('state', '!=', 'draft'),
            ]
            if restrict_goal_ids:
                domain.append(('ids', 'in', restrict_goal_ids))
            else:
                # if no subset goals, use the dates for restriction
                if start_date:
                    domain.append(('start_date', '=', start_date))
                if end_date:
                    domain.append(('end_date', '=', end_date))

            if challenge.visibility_mode == 'personal':
                if not user_id:
                    raise osv.except_osv(_('Error!'), _("Retrieving progress for personal challenge without user information"))
                domain.append(('user_id', '=', user_id))
                sorting = goal_obj._order
                limit = 1
            else:
                line_data.update({
                    'own_goal_id': False,
                    'goals': [],
                })
                sorting = "completeness desc, current desc"
                limit = False

            goal_ids = goal_obj.search(cr, uid, domain, order=sorting, limit=limit, context=context)
            ranking = 0
            for goal in goal_obj.browse(cr, uid, goal_ids, context=context):
                definition_id = goal.definition_id  # new stuff
                evaled_domain = safe_eval(definition_id.domain, {'user': goal.user_id})
                evaled_domain = str(evaled_domain)
                if challenge.visibility_mode == 'personal':
                    # limit=1 so only one result
                    line_data.update({
                        'id': goal.id,
                        'current': goal.current,
                        'completeness': goal.completeness,
                        'state': goal.state,
                        'domain': evaled_domain,
                        'model': definition_id.model_id.model,
                    })
                    if goal.state != 'reached':
                        all_reached = False
                else:
                    ranking += 1
                    if user_id and goal.user_id.id == user_id:
                        line_data['own_goal_id'] = goal.id
                    elif restrict_top and ranking > restrict_top:
                        # not own goal and too low to be in top
                        continue

                    line_data['goals'].append({
                        'id': goal.id,
                        'user_id': goal.user_id.id,
                        'name': goal.user_id.name,
                        'rank': ranking,
                        'current': goal.current,
                        'completeness': goal.completeness,
                        'state': goal.state,
                        'domain': evaled_domain,
                        'model': definition_id.model_id.model,
                    })
                    if goal.state != 'reached':
                        all_reached = False
            if goal_ids:
                res_lines.append(line_data)
        if all_reached and not challenge.show_reached:  # new stuff
            return []
        if challenge.precision:
            for line in res_lines:
                current = line.get('current')
                if current:
                    current = round(current / challenge.precision) * challenge.precision
                    line['current'] = current
        return res_lines
