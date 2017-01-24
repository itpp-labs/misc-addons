# -*- coding: utf-8 -*-

from openerp import models, fields


class ProjectProjectAutostaging(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'autostaging.folder']


class ProjectTaskTypeAutostaging(models.Model):
    _name = 'project.task.type'
    _inherit = ['project.task.type', 'autostaging.stage']
    _card_model = 'project.task'
    _card_stage_id = 'stage_id'
    autostaging_next_stage = fields.Many2one('project.task.type', string='Autostaging next stage')


class ProjectTaskAutostaging(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'autostaging.card']
    _field_folder_id = 'project_id'
    _field_stage_id = 'stage_id'

    autostaging_next_stage = fields.Many2one('project.task.type', string='Autostaging next stage', related='stage_id.autostaging_next_stage')
    _track = {
        'stage_id': {
            'ProjectTaskAutostaging.mt_autostaging':
            lambda self, cr, uid, obj, ctx=None:
            ctx and ctx.get('autostaging')
        }
    }
