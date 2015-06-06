# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class project_project_auto_staging(models.Model):
    _inherit = 'project.project'
    allow_automove = fields.Boolean('Allow automove', default=False)


class autostaging(models.Model):
    _name = 'project_task_auto_staging.autostaging'

    testing_stage = fields.Char(string='Testing Stage')
    done_stage = fields.Char(string='Done Stage')
    cancell_stage = fields.Char(string='Cancell Stage')
    delay_done = fields.Integer(string='Delay Done Stage')
    delay_cancell = fields.Integer(string='Delay Cancel Stage')


class project_task_auto_staging(models.Model):
    _inherit = 'project.task'
    allow = fields.Boolean(compute='_get_allow' )
    delay = fields.Integer(
        string='Delay', compute='_get_delay_done')
    to_stage = fields.Char(
        string='To stage', compute='_get_stage')
    when_date = fields.Date(compute='_get_when_date')


    def create_message(self):
        message_vals = {
                        'body': 'TEST MSG',
                        'date': datetime.datetime.now(),
                        'res_id': 1,
                        'record_name': 'icking_name',
                        'model': 'project.task',
                        'type': 'comment',
                        }
        self.env['mail.message'].sudo().create(message_vals)
        print "\n\n MSG \n\n"
        for r in self.env['mail.message']: print r
   

    def move_to_stage(self, task):
            print "\n MOVE_TO_STAGE \n"
            self.create_message()
            ptt_env = self.env['project.task.type']
            stage = ptt_env.search([['name', '=', task.to_stage]])
            #task.write({'stage_id': stage.id});

    @api.model
    def move_tasks(self):
        today = fields.Date.context_today(self)
        pt_env = self.env['project.task']
        tasks = pt_env.search([])
        for task in tasks:
            print "\n MOVE_TASK \n"
            if task.allow and today == task.when_date or True:
                self.move_to_stage(task)

   

    """
    @api.cr_uid_ids_context
    def my_test(self, cr, uid, ids, context):
        recipient_partners = []
        recipient_partners.append(1)
        post_vars = {'subject': "notification about order",
            'body': "Yes inform me as i belong to manfacture group",
            'partner_ids': recipient_partners,} 
        thread_pool = self.pool.get('mail.thread')
        thread_pool.message_post(
            cr, uid, False,
            type="notification",
            subtype="mt_comment",
            context=context,
            **post_vars)

    """

    def _get_when_date(self):
        delta = datetime.timedelta(days=self.delay)
        self.when_date = datetime.datetime.strptime(
            self.write_date, DEFAULT_SERVER_DATETIME_FORMAT) + delta

    def _get_allow(self):
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        if not self.project_id.allow_automove or \
           self.stage_id.name == records[0].done_stage or \
           self.stage_id.name == records[0].cancell_stage:
            self.alow = False
        else:
            self.allow = True

    def _get_delay_done(self):
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        if self.stage_id.name == records[0].testing_stage:
            self.delay = records[0].delay_done
        else:
            self.delay = records[0].delay_cancell

    def _get_stage(self):
        as_env = self.env['project_task_auto_staging.autostaging']
        records = as_env.search([])
        if self.stage_id.name == records[0].testing_stage:
            self.to_stage = records[0].done_stage
        else:
            self.to_stage = records[0].cancell_stage

    @api.model
    def get_current_stage(self, stageID):
        return self.stage_id.browse([stageID]).name


"""
class task(models.Model):
    _inherit = 'project.task'
    automove_stage = fields.Char(
        readonly=True, compute='_compute_automove_fields')
    automove_delay = fields.Integer(
        string='automove delay', readonly=True,
        compute='_compute_automove_fields')

    @api.one
    def _compute_automove_fields(self):
        if self.stage_id.name == 'Testing':
            self.automove_stage = 'Done'
            self.automove_delay = 7
        elif (self.stage_id.name not in ('Cancell', 'Done')):
            self.automove_stage = 'Cancell'
            self.automove_delay = 20
"""
