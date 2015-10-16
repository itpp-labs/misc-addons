# -*- coding: utf-8 -*-

from openerp import models, fields


class ProjectProjectAutostaging(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'autostaging.folder']


class ProjectTaskTypeAutostaging(models.Model):
    _name = 'project.task.type'
    _inherit = ['project.task.type', 'autostaging.stage']

    next_stage = fields.Many2one('project.task.type', string='Next stage')


class ProjectTaskAutostaging(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'autostaging.task']

    next_stage = fields.Many2one('project.task.type', string='Next stage', related='stage_id.next_stage')
    # _track = {
    #     'stage_id': {
    #         'project_task_auto_staging.mt_auto_move_task':
    #         lambda self, cr, uid, obj, ctx=None:
    #             ctx and ctx.get('auto_staging')
    #     }
    # }
