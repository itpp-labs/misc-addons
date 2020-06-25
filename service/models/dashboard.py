from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval
import datetime


class DashBoard(models.Model):

    _name = 'service_drm.dashboard'

    @api.multi
    def _compute_count_operations(self):
        for r in self:
            r._compute_count_operations_one()

    action_id = fields.Many2one('ir.actions.act_window', string='Action')
    url = fields.Char('Image URL')
    sequence = fields.Integer('Sequence')
    color = fields.Integer('Color')
    name = fields.Char('Name', translate=True)
    date_start = fields.Datetime('Date')
    date_stop = fields.Datetime('Date_stop')
    count_record = fields.Integer(string='# Record')
    display_inline_image = fields.Boolean('Display Inline Image in Kanban ?')
    display_outline_image = fields.Boolean('Display Outline Image in Kanban ?')
    display_record_count = fields.Boolean(
        'Display Number of records in Kanban ?')

    technician_name = fields.Many2one(
        comodel_name='hr.employee', domain=[('name', 'ilike',
                                             'Technician')], string="Technician")
    use_orders = fields.Boolean(
        'Orders', help="Check this box to manage Orders")
    use_lift = fields.Boolean(
        'Lift', help="Check this box to manage lift")
    use_work_order = fields.Boolean(
        'Work_order', help="Check this box to manage work Orders")
    use_warrenty_order = fields.Boolean(
        'Warrenty Orders', help="Check this box to manage Warrenty Orders")
    use_inspection = fields.Boolean(
        'Inspection', help="Check this box to manage Inspection")
    use_calender = fields.Boolean('Calender')

    use_pickup = fields.Boolean(
        'Pickup', help="Check this box to manage pickup")
    use_delivery = fields.Boolean(
        'Delivery', help="Check this box to manage Delivery")
    count_orders = fields.Integer(
        "Count Repair Orders", compute="compute_count_all")  # all done orders
    count_orders_pending = fields.Integer(
        "Count all Pending Orders", compute="compute_count_all")  # all pending orders
    count_orders_repair = fields.Integer(
        "Count Pending Repair Orders", compute="compute_count_all")
    count_orders_comeback = fields.Integer(
        "Count comeback Orders", compute="compute_count_all")
    count_orders_pdi = fields.Integer(
        "Count pdi Orders", compute="compute_count_all")
    count_lift = fields.Integer(
        "Count lift", compute="compute_count_all")
    count_lift_pending = fields.Integer(
        "Count lift Pending", compute="compute_count_all")

    count_work_order = fields.Integer(
        "Count work order", compute="compute_count_all")
    count_work_order_pending = fields.Integer(
        "Count work order Pending", compute="compute_count_all")
    count_warranty_order = fields.Integer(
        "Count warrenty Order", compute="compute_count_all")
    count_inspection = fields.Integer(
        "Count Inspection", compute="compute_count_all")
    count_pickup = fields.Integer("Count Pickup", compute="_compute_count_all")
    count_pickup_pending = fields.Integer(
        "Count Pickup Pending", compute="compute_count_all")
    count_pickup_cancelled = fields.Integer(
        "Count Canceled", compute="compute_count_all")

    count_delivery = fields.Integer("Count Delivered", compute="_compute_count_all")
    count_delivery_pending = fields.Integer(
        "Count Deliveryp Pending", compute="compute_count_all")
    count_delivery_cancelled = fields.Integer(
        "Count Delivery Canceled", compute="compute_count_all")
    count_quote = fields.Integer(
        "Count QUOTE", compute="compute_count_all")



    @api.model
    def compute_count_all(self):
        # count records of reapir order
        drm_repair_order_obj = self.env['service.repair_order']
        for record in self:
            orders = drm_repair_order_obj.search(
                [('warranty', '!=', True), ('state', 'in', ['done'])])
            record.count_orders = len(orders.ids)

            orders = drm_repair_order_obj.search(
                [('state', 'in', ['QUOTE'])])
            record.count_quote = len(orders.ids)

            orders_pending = drm_repair_order_obj.search(
                [('state', 'not in', ['done','CANCEL'])])
            record.count_orders_pending = len(orders_pending.ids)

            orders_repair = drm_repair_order_obj.search(
            [('repair_type', 'in', ['repair_order']), ('warranty', '!=', True)])
            record.count_orders_repair = len(orders_repair.ids)

            orders_comeback = drm_repair_order_obj.search(
                [('repair_type', 'in', ['comeback'])])
            record.count_orders_comeback = len(orders_comeback.ids)

            orders_pdi = drm_repair_order_obj.search(
                [('repair_type', 'in', ['pdi'])])
            record.count_orders_pdi = len(orders_pdi.ids)

            warranty_order = drm_repair_order_obj.search(
                [('state', 'in', ['draft', 'confirm'])])
            record.count_warranty_order = len(warranty_order.ids)

            cancel = drm_repair_order_obj.search(
                [('state', 'in', ['CANCEL'])])
            record.count_cancel = 0
        # count records of lift
        drm_lift_obj = self.env['drm.lift']
        for record in self:
            lifts = drm_lift_obj.search(
                [('working_state', 'in', ['done'])])
            record.count_lift = len(lifts.ids)
            lifts_pending = drm_lift_obj.search(
                [('working_state', 'in', ['normal', 'blocked'])])
            record.count_lift_pending = len(lifts_pending.ids)
        # count work order
        drm_work_order_obj = self.env['drm.workorders']
        for record in self:
            work_orders = drm_work_order_obj.search(
                [('state', 'in', ['done', 'cancle'])])
            record.count_work_order = len(work_orders.ids)
            work_orders_pending = drm_work_order_obj.search(
                [('state', 'in', ['progress', 'pending', 'ready'])])
            record.count_work_order_pending = len(work_orders_pending.ids)
        # count 30 point Inspection
        drm_inspection_obj = self.env['service.inspection']
        for record in self:
            inspection = drm_inspection_obj.search(
                [('state', 'in', ['draft', 'progress', 'done', 'cancel'])])
            record.count_inspection = len(inspection.ids)
        # count pickup and delivery
        drm_pickup_obj = self.env['drm.pickup']
        for record in self:
            pickup = drm_pickup_obj.search(
                [('state', 'in', ['done']),('process_type', '=', 'pickup')])
            record.count_pickup = len(pickup.ids)
            pickup_pending = drm_pickup_obj.search(
                [('state', 'in', ['confirm', 'progress']),('process_type', '=', 'pickup')])
            record.count_pickup_pending = len(pickup_pending.ids)
            pickup_cancel = drm_pickup_obj.search(
                [('state', 'in', ['cancel']),('process_type', '=', 'pickup')])
            record.count_pickup_cancelled = len(pickup_cancel.ids)

        for record in self:
            delivery = drm_pickup_obj.search(
                [('state', 'in', ['done']),('process_type', '=', 'delivery')])
            record.count_delivery = len(delivery.ids)
            delivery_pending = drm_pickup_obj.search(
                [('state', 'in', ['confirm', 'progress']),('process_type', '=', 'delivery')])
            record.count_delivery_pending = len(delivery_pending.ids)
            delivery_cancel = drm_pickup_obj.search(
                [('state', 'in', ['cancel']),('process_type', '=', 'delivery')])
            record.count_delivery_cancelled = len(delivery_cancel.ids)


        records={}
        drm_repair_order_obj = self.env['service.repair_order']
        
        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['QUOTE'])])
        records['count_quote'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['APPROVE'])])
        records['count_approve'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['PARTS'])])
        records['count_parts'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['PICKUP'])])
        records['count_pickups'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['INSPECT'])])
        records['count_inspect'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['LIFT'])])
        records['count_lift'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['TEST'])])
        records['count_test'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['COMPLETE'])])
        records['count_complete'] = len(cnt.ids)

        cnt = drm_repair_order_obj.search(
                [('state', 'in', ['DELIVER'])])
        records['count_deliver'] = len(cnt.ids)

        #_____________________REPAIR-ORDERS___________________________________________
        orders_repair = drm_repair_order_obj.search(
            [('repair_type', '=', 'repair_order')])
        records['count_orders_repair'] = len(orders_repair)

        orders_repair_done = drm_repair_order_obj.search(
            [('repair_type', 'in', ['repair_order']), ('state', 'in', ['done'])])
        records['count_repair_done'] = len(orders_repair_done.ids)

        orders_repair_pending = drm_repair_order_obj.search(
            [('repair_type', '=', 'repair_order'),('state', 'not in', ['done','CANCEL'])])
        records['orders_repair_pending'] = len(orders_repair_pending)
        

        orders_repair_cancel = drm_repair_order_obj.search(
            [('repair_type', 'in', ['repair_order']), ('state', 'in', ['CANCEL'])])
        records['orders_repair_cancel'] = len(orders_repair_cancel.ids)
        #_____________________________________________________________________________

        drm_work_order_obj=self.env['drm.workorders']

        #______________________BUG FIX NEEDED_______________________________________

        technicians_id_obj=self.env['hr.department'].search(
                [('name', 'ilike','Technician')])
        


        technicians_id=""
        for i in range(len(technicians_id_obj)):
            technicians_id=technicians_id_obj[i].id
        

        technicians=self.env['hr.employee'].search(
                [('department_id', '=',technicians_id)])
        records['counts_technicians']=len(technicians)

        work_assigned=drm_work_order_obj.search(
            [('mechanic_id','!=',None)])
        records['work_assigned']=len(work_assigned)

        work_assigned_pending=drm_work_order_obj.search(
            [('state', 'not in', ['cancel','done']),('mechanic_id','!=',None)])
        records['counts_technicians_work_pending']=len(work_assigned_pending)

        work_assigned_Done=drm_work_order_obj.search(
            [('state', 'in', ['done']),('mechanic_id','!=',None)])
        records['counts_technicians_work_done']=len(work_assigned_Done)

        work_assigned_cancel=drm_work_order_obj.search(
            [('state', 'in', ['cancel']),('mechanic_id','!=',None)])
        records['counts_technicians_work_cancel']=len(work_assigned_cancel)

        technicians_hour=0
        for i in range(len(technicians)):
            technicians_hour+=technicians[i].total_time

        technicians_mins=technicians_hour*60*7
        
        #_____________________WORDORDERS___________________________________________

        
        orders_work = drm_work_order_obj.search(
            [])
        records['count_orders_work'] = len(orders_work.ids)

        orders_work_done = drm_work_order_obj.search(
            [('state', 'in', ['done'])])
        records['count_work_done'] = len(orders_work_done.ids)

        orders_work_pending = drm_work_order_obj.search(
            [('state', 'not in', ['done','cancel'])])
        records['orders_work_pending'] = len(orders_work_pending.ids)

        orders_work_cancel = drm_work_order_obj.search(
            [('state', 'in', ['cancel'])])
        records['orders_work_cancel'] = len(orders_work_cancel.ids)


        total_working_hours_obj=drm_work_order_obj.search(
            [('state', 'not in', ['cancel','done']),('mechanic_id','!=',None),('duration_expected','!=',None)])
        total_working_hours=0
        for i in range(len(total_working_hours_obj)):
            total_working_hours+=total_working_hours_obj[i].duration_expected

        if technicians_mins==0:
            load_percent=0
        else:
            load_percent=(total_working_hours/technicians_mins)*100
            load_percent=round(load_percent)
        
        
        records['load_percent']=str(load_percent)+"%"
        if load_percent<=50:
            records['load_color']="#00B30D"
        elif load_percent>50 and load_percent<80:
            records['load_color']="#E0BA19"
        else:
            records['load_color']="#E8451E"

        test=self.env['res.groups'].search([('name', 'in', ['User: Access Own Documents Only'])])
        user_obj=test.users
        
        for i in range(len(user_obj)):
            if self.env.user.id==user_obj[i].id:
                flag="True"
                records['technician_flag']=flag
            else:
                flag="false"
        efficiency=0
        dept=technicians = self.env['hr.department'].search(
            [('name','=','Technician')])
        technicians = self.env['hr.employee'].search(
            [('department_id','=',dept.id)])
        for i in range(len(technicians)):
            efficiency = efficiency+technicians[i].efficiency

        if efficiency == 0.0:
            efficiency = 0
        else:
            efficiency = (float(efficiency))/float(len(technicians))
        records['efficiency']=efficiency
        
        # flag = self.env.user.has_group('base.group_user') and self.env.user.has_group('base.user_root')
        

        
        #____________________________________________________________________________
        return records

