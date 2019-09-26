odoo.define('hr_dashboard.dashboard', function (require) {
"use strict";

var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var HrDashboardView = AbstractAction.extend(ControlPanelMixin, {
	events: {
		'click .leaves-left': 'leaves_left',
        'click .payslip': 'action_payslip',
        'click .timesheet': 'action_timesheet_user',
        'click .contract': 'action_contract',
        'click .leaves_to_approve': 'action_leaves_to_approve',
        'click .timesheets_to_approve': 'action_timesheets',
        'click .job_applications': 'action_job_applications',
        'click .leave_allocations': 'action_leave_allocations',
        'click .attendance': 'action_attendance',
        'click .expenses': 'action_expenses',
        'click #generate_payroll_pdf': function(){this.generate_payroll_pdf("bar");},
        'click #generate_attendance_pdf': function(){this.generate_payroll_pdf("pie")},
        'click .my_profile': 'action_my_profile',
	},
	init: function(parent, context) {
        this._super(parent, context);
        var employee_data = [];
        var self = this;
        if (context.tag == 'hr_dashboard.dashboard') {
            self._rpc({
                model: 'hr.dashboard',
                method: 'get_employee_info',
            }, []).then(function(result){
                self.employee_data = result[0]
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var hr_dashboard = QWeb.render( 'hr_dashboard.dashboard', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(hr_dashboard).prependTo(self.$el);
        self.graph();
        self.previewTable();
        return hr_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },
    leaves_left: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Leaves"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            src_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_employee_id': [self.employee_data.id],
                    'default_employee_id': self.employee_data.id,
                    'search_default_group_type': true,
                    'search_default_year': true
                    },
            domain: [['holiday_type','=','employee'], ['state','!=', 'refuse']],
            search_view_id: self.employee_data.leave_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_payslip: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Payslips"),
            type: 'ir.actions.act_window',
            res_model: 'hr.payslip',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_employee_id': [self.employee_data.id],
                    'default_employee_id': self.employee_data.id,
                    },
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_timesheet_user: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Timesheets"),
            type: 'ir.actions.act_window',
            res_model: 'account.analytic.line',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_employee_id': [self.employee_data.id],
//                    'search_default_month': true,
                    },
            domain: [['project_id', '!=', false]],
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_contract: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'hr.contract',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list']],
            context: {
                    'search_default_employee_id': [self.employee_data.id],
                    'default_employee_id': self.employee_data.id,
                    },
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_leaves_to_approve: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Department Leaves"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar,kanban,activity',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'calendar'],[false, 'kanban'],[false, 'activity']],
            context: {
                    'search_default_approve': true,
                    },
            search_view_id: self.employee_data.leave_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_timesheets: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("All Timesheets"),
            type: 'ir.actions.act_window',
            res_model: 'account.analytic.line',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_week': true,
                    'search_default_groupby_employee': true,
                    'search_default_groupby_project': true,
                    'search_default_groupby_task': true,
                    },
            domain: [['project_id', '!=', false]],
            search_view_id: self.employee_data.timesheet_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_job_applications: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Applications"),
            type: 'ir.actions.act_window',
            res_model: 'hr.applicant',
            view_mode: 'kanban,tree,form,pivot,graph,calendar',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form'],
                    [false, 'pivot'],[false, 'graph'],[false, 'calendar']],
            context: {},
            search_view_id: self.employee_data.job_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_leave_allocations: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Department Leaves Allocation"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave.allocation',
            view_mode: 'tree,form,kanban,activity',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban'],[false, 'activity']],
            context: {
                    'search_default_approve': true,
                    },
//            domain: [['type','=','add'],],
            search_view_id: self.employee_data.leave_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}}).then(function(){framework.unblockUI();})
    },
    action_attendance: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Attendances"),
            type: 'ir.actions.act_window',
            res_model: 'hr.attendance',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {
                    'search_default_check_in_filter': 'today',
                    },
            domain: [],
            search_view_id: self.employee_data.attendance_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_expenses: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Expense Reports to Approve"),
            type: 'ir.actions.act_window',
            res_model: 'hr.expense.sheet',
            view_mode: 'tree,kanban,form,pivot,graph',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form'],[false, 'kanban'],[false, 'pivot'],[false, 'graph']],
            context: {
                    'search_default_submitted': true,
                    },
            domain: [],
            search_view_id: self.employee_data.attendance_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_my_profile: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("My Profile"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: self.employee_data.id,
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            context: {'edit': true},
            domain: [],
            target: 'inline'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    // Here we are plotting bar,pie chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#myChart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                // "October", "November", "December"],
                labels: self.employee_data.payroll_label,
                datasets: [{
                    label: 'Payroll',
                    data: self.employee_data.payroll_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.employee_data.payroll_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.employee_data.
                            payroll_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.employee_data.payroll_dataset.length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
        //Pie Chart
        var piectx = this.$el.find('#attendanceChart');
        bg_color_list = []
        for (var i=0;i<=self.employee_data.attendance_dataset.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.employee_data.attendance_dataset,
                    backgroundColor: bg_color_list,
                    label: 'Attendance Pie'
                }],
                labels:self.employee_data.attendance_labels,
            },
            options: {
                responsive: true
            }
        });

    },
    previewTable: function() {
        $('#emp_details').DataTable( {
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Employee Details',
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },
                {
                    extend: 'print',
                    exportOptions: {
                    columns: ':visible'
                    }
                },
            'colvis'
            ],
            columnDefs: [ {
                targets: -1,
                visible: false
            } ],
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            pageLength: 15,
        } );
    },
    generate_payroll_pdf: function(chart) {
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChart');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#attendanceChart');
        }

        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('report.pdf');
    },

});
core.action_registry.add('hr_dashboard.dashboard', HrDashboardView);
return HrDashboardView
});