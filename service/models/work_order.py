# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning


class RepairWorkorders(models.Model):
    _name = "drm.workorders"
    _inherit = ['mail.thread']
    _description = "Create Workorders"

    name = fields.Char(string='Work Order',
                       required=True,
                       default="New",
                       states={'done': [('readonly', True)],
                               'cancel': [('readonly', True)]})

    workcenter_id = fields.Many2one('drm.lift',
                                    'Lifts(work center)',
                                    required=False,
                                    states={'done': [('readonly', True)],
                                            'cancel': [('readonly', True)]})
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string='End Date')

    working_state = fields.Selection('Workcenter Status',
                                     related='workcenter_id.working_state',
                                     help='Technical: used in views only')

    repair_order_id = fields.Many2one(comodel_name='service.repair_order',
                                      string='Repair Order',
                                      required=True,
                                      states={
                                          'ready': [('readonly', True)],
                                          'progress': [('readonly', True)],
                                          'done': [('readonly', True)],
                                          'cancel': [('readonly', True)]}
                                      )

    standard_job_id = fields.Many2one(comodel_name='service.standard_job',
                                      string="Standard Job",
                                      required=True)

    vehicle_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                 string='Vehicle',
                                 required=True,
                                 readonly=False)

    state = fields.Selection([('pending', 'Pending'),
                              ('ready', 'Ready'),
                              ('progress', 'In Progress'),
                              ('done', 'Finished'),
                              ('cancel', 'Cancelled')],
                             string='Status',
                             default='pending')

    date_planned_start = fields.Datetime('Scheduled Start Date',
                                         states={'done': [('readonly', True)],
                                                 'cancel': [('readonly', True)]})

    date_planned_finished = fields.Datetime('Scheduled Finish Date',
                                            states={'done': [('readonly', True)],
                                                    'cancel': [('readonly', True)]})

    date_start = fields.Datetime('Effective Start Date',
                                 states={'done': [('readonly', True)],
                                         'cancel': [('readonly', True)]})

    date_finished = fields.Datetime('Effective End Date',
                                    states={'done': [('readonly', True)],
                                            'cancel': [('readonly', True)]})

    duration_expected = fields.Float('Expected Duration', digits=(16, 2),
                                     states={'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]},
                                     help="Expected duration (in minutes)")

    duration = fields.Float('Real Duration',
                            compute='_compute_duration',
                            readonly=True, store=True)

    duration_percent = fields.Integer('Duration Deviation (%)',
                                      compute='_compute_duration',
                                      group_operator="avg", readonly=True, store=True)

    mechanic_id = fields.Many2one(comodel_name='hr.employee',
                                  string='Mechanic',
                                  readonly=False,
                                  required=False,)

    customer_id = fields.Many2one(comodel_name='res.partner',
                                  string='Customer',
                                  readonly=False,
                                  required=False,
                                  )
    # Should be used differently as BoM can change in the meantime
    # operation_id = fields.Many2one('mrp.routing.workcenter', 'Operation')

    worksheet = fields.Binary(
        'Worksheet', related='standard_job_id.document', readonly=True)

    time_ids = fields.One2many('drm.workcenter.productivity', 'workorder_id')
    is_complete = fields.Boolean(string='Completed')
    is_pause = fields.Boolean(string='Paused')

    is_user_working = fields.Boolean('Is Current User Working',
                                     compute='_compute_is_user_working',
                                     help="Technical field indicating whether the current user is working. ")

    next_work_order_id = fields.Many2one('drm.workorders', "Next Work Order")

    # production_date = fields.Datetime('Production Date', related='production_id.date_planned_start', store=True)

    @api.onchange('workcenter_id')
    def on_change_workcenter(self):
        self.mechanic_id = self.workcenter_id.mechanic_id.id

    @api.onchange('start_date', 'end_date')
    def on_change_start_date(self):
        if self.state != 'done':
            lift = self.env['drm.workorders'].search([('workcenter_id', '=', self.workcenter_id.id), ('start_date', '>=', self.start_date), (
                'end_date', '<=', self.start_date), ('start_date', '>=', self.end_date), ('end_date', '<=', self.end_date)])
            if lift:
                self.start_date = False
                self.end_date = False
                raise Warning(
                    _("You can't work on this LIFT for %s - %s") % (lift.start_date, lift.end_date))

    @api.model
    def create(self, vals):
        return super(RepairWorkorders, self).create(vals)

    @api.model
    def default_get(self, vals):
        """
        In this function default_service_event is checked
        and added by default in form view
        """
        res = super(RepairWorkorders, self).default_get(vals)
        if not res.get('repair_order_id') and self.env.context.get('active_id')\
                and self.env.context.get('active_model') == 'service.repair_order' \
                and self.env.context.get('active_id'):
            res['repair_order_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).id
            res['vehicle_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).major_unit_id.id
            res['mechanic_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).mechanic_id.id
            res['customer_id'] = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1).partner_id.id

        if not res.get('partner_id') and self.env.context.get('active_id') and \
                self.env.context.get('active_model') == 'service.repair_order' and \
                self.env.context.get('active_id'):
            temp = self.env['service.repair_order'].search(
                [('id', '=', self.env.context['active_id'])], limit=1)
            if 'workorders' in self.env.context.keys():
                res['standard_job_id'] = self.env.context['workorders']
        return res

    def _compute_is_user_working(self):
        """ Checks whether the current user is working """
        for order in self:
            if order.time_ids.filtered(lambda x: (x.user_id.id == self.env.user.id)
                                       and (not x.date_end)
                                       and (x.loss_type in ('productive', 'performance'))):
                order.is_user_working = True
            else:
                order.is_user_working = False

    @api.one
    @api.depends('time_ids.duration')
    def _compute_duration(self):
        self.duration = sum(self.time_ids.mapped('duration'))
        if self.duration_expected:
            self.duration_percent = 100 * \
                (self.duration_expected - self.duration) / \
                self.duration_expected
        else:
            self.duration_percent = 0

    @api.multi
    def button_start(self):
        # TDE CLEANME
        timeline = self.env['drm.workcenter.productivity']
        if self.duration < self.duration_expected:
            loss_id = self.env['drm.workcenter.productivity.loss'].search(
                [('loss_type', '=', 'productive')], limit=1)
            if not len(loss_id):
                raise UserError(
                    _("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        else:
            loss_id = self.env['drm.workcenter.productivity.loss'].search(
                [('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(
                    _("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        for workorder in self:
            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ') + self.env.user.name,
                'loss_id': loss_id[0].id,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })

        self.write({'state': 'progress',
                    'date_start': datetime.now(),
                    'is_pause': False,
                    })

    @api.multi
    def button_finish(self):
        self.ensure_one()
        self.end_all()
        self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
        if self.repair_order_id.pickup_workorder_count == self.repair_order_id.repair_workorder_done_count \
                and self.repair_order_id.state == 'LIFT':
            self.repair_order_id.write({'state': 'TEST',
                                        'lift_date': datetime.now()})
        technicians = self.env['hr.employee'].search(
            [('id', '=', self.mechanic_id.id)])
        efficiency = technicians.efficiency
        emp_productivity = 0
        emp_productivity_obj = self.env['drm.workcenter.productivity'].search(
            [('workorder_id', '=', self.id)])
        for i in range(len(emp_productivity_obj)):
            emp_productivity += emp_productivity_obj[i].duration
        std_job_obj = self.env['service.standard_job'].search(
            [('id', '=', self.standard_job_id.id)])
        std_job_hour = std_job_obj.hours
        std_job_min = float(std_job_hour)*60
        emp_productivity = emp_productivity
        eff = (std_job_min/float(emp_productivity))*100
        if efficiency == 0.0:
            efficiency = float(eff)
        else:
            efficiency = (float(efficiency)+float(eff))/2
        self._cr.execute("update hr_employee set efficiency=" +
                         str(efficiency)+" where id="+str(self.mechanic_id.id))

    @api.multi
    def end_previous(self, doall=False):
        """
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        timeline_obj = self.env['drm.workcenter.productivity']
        domain = [('workorder_id', 'in', self.ids), ('date_end', '=', False)]
        if not doall:
            domain.append(('user_id', '=', self.env.user.id))
        for timeline in timeline_obj.search(domain, limit=None if doall else 1):
            wo = timeline.workorder_id
            if timeline.loss_type != 'productive':
                timeline.write({'date_end': fields.Datetime.now()})
            else:
                maxdate = fields.Datetime.from_string(
                    timeline.date_start) + relativedelta(minutes=wo.duration_expected - wo.duration)
                enddate = datetime.now()
                if maxdate > enddate:
                    timeline.write({'date_end': enddate})
                else:
                    timeline.write({'date_end': maxdate})
                    loss_id = self.env['drm.workcenter.productivity.loss'].search(
                        [('loss_type', '=', 'performance')], limit=1)
                    if not len(loss_id):
                        raise UserError(
                            _("You need to define at least one unactive productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
                    timeline.copy(
                        {'date_start': maxdate, 'date_end': enddate, 'loss_id': loss_id.id})

    @api.multi
    def end_all(self):
        return self.end_previous(doall=True)

    @api.multi
    def button_ready(self):
        if self.repair_order_id.state != 'LIFT':
            raise Warning(
                _("You can't start the work order until the repair order is in the LIFT state!!!"))
        if not self.workcenter_id.id:
            raise Warning(
                _('Please select the lift which is free !!!'))
        if self.mechanic_id.priority < self.standard_job_id.priority:
            raise Warning(
                _('Please select the mechanic with level higher or equal to standard job level !!!'))
        else:
            self.write({'state': 'ready'})

    @api.multi
    def button_pending(self):
        self.end_previous()
        self.write({'is_pause': True})

    @api.multi
    def button_unblock(self):
        for order in self:
            order.workcenter_id.unblock()

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def button_done(self):
        if any([x.state in ('done', 'cancel') for x in self]):
            raise UserError(
                _('A Manufacturing Order is already done or cancelled!'))
        self.end_all()
        self.write({'state': 'done',
                    'date_finished': datetime.now()})
