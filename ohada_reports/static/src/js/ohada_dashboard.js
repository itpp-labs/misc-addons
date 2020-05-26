odoo.define('ohada_dashboard.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var _t = core._t;
var QWeb = core.qweb;


var OhadaDashboard = AbstractAction.extend(ControlPanelMixin, {
    template: 'OhadaDashboardMain',
    cssLibs: [
        '/web/static/lib/nvd3/nv.d3.css'
    ],
    jsLibs: [
        '/web/static/lib/nvd3/d3.v3.js',
        '/web/static/lib/nvd3/nv.d3.js',
        '/web/static/src/js/libs/nvd3.js'
    ],
    events: {
        'change #change_year': 'change_year',
        'change #change_all_entries': 'change_all_entries',
        'click .print_bundle': 'print_bundle',
        'click .close': 'close_popup',
        'click .export_pdf': 'print_bundle_pdf',
        'click .export_xlsx': 'print_bundle_xlsx',
        'click .print_bs_pdf': 'print_bs_pdf',
        'click .print_lands_bs_pdf': 'print_lands_bs_pdf',
        'click .print_pl_pdf': 'print_pl_pdf',
        'click .print_cf_pdf': 'print_cf_pdf',
        'click .open_report': 'open_report',
    },

    open_report: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        self.data.options.date.filter = 'custom';
        return self.do_action({
            name: event.target.getAttribute('name'),
            tag: 'ohada_report',
            type: 'ir.actions.client',
            context: {
                id : parseInt(event.target.getAttribute('report-id')),
                model : 'ohada.financial.html.report',
                report_options : self.data['options'],
            },
        },{on_reverse_breadcrumb: function(){ return self.update_cp();}});
    },

    fetch_data: function(year=false, all_entries=false) {
        var self = this;
        var def1 = this._rpc({
                model: 'ohada.dashboard',
                method: 'fetch_data',
                args: [year, all_entries],
        }).done(function(result) {
            self.data =  result;
        });
        return $.when(def1);
    },

    update_cp: function() {
        var self = this;
        var status = {
            cp_content: {$searchview_buttons: self.data['search_panel']},
        };
        this.update_control_panel(status, {clear: true});
    },

    close_popup: function(){
        document.getElementById("myForm").style.display = "none";
        document.getElementById("modal-backdrop").style.display = "none";
    },
    change_year: function(ev) {
        var self = this;
        this.fetch_data(parseInt(ev['currentTarget']['value']), self.data['options']['all_entries']).then(function() {
            self._updateTemplateBody();
        });
    },
    change_all_entries: function(ev) {
        var self = this;
        var entries_value = (ev['currentTarget']['value'] == 'True');
        this.fetch_data(this.data['this_year'], entries_value).then(function() {
            self._updateTemplateBody();
        });
    },
    print_lands_bs_pdf: function() {
        var self = this;
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: {"model": 'ohada.financial.html.report',
                    "options": JSON.stringify(self.data['options']),
                    "financial_id": self.data['bs_id'],
                    "output_format": "pdf",
                    "horizontal": "True"},
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },
    print_bs_pdf: function() {
        var self = this;
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: {"model": 'ohada.financial.html.report',
                    "options": JSON.stringify(self.data['options']),
                    "financial_id": self.data['bs_id'],
                    "output_format": "pdf"},
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },
    print_pl_pdf: function() {
        var self = this;
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: {"model": 'ohada.financial.html.report',
                    "options": JSON.stringify(self.data['options']),
                    "financial_id": self.data['pl_id'],
                    "output_format": "pdf"},
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },
    print_cf_pdf: function() {
        var self = this;
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: {"model": 'ohada.financial.html.report',
                    "options": JSON.stringify(self.data['options']),
                    "financial_id": self.data['cf_id'],
                    "output_format": "pdf"},
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },
    print_bundle: function() {
        document.getElementById("myForm").style.display = "block";
        document.getElementById("modal-backdrop").style.display = "block";
    },

    print_bundle_xlsx: function() {
        var self = this;
        var checked_reports = [];
        this.$('.bundle_item input:checked').each(function() {
            checked_reports.push($(this)[0].dataset['recordId']);
        });
        if(checked_reports.length == 0){
            return true;
        }
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: {"model": "ohada.financial.html.report",
                   "options": JSON.stringify(self.data['options']),
                   "financial_id": 3,
                   "output_format": "xlsx_bundle",
                   "bundle_items": checked_reports},
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },

    print_bundle_pdf: function() {
        var self = this;
        var checked_reports = [];
        this.$('.bundle_item input:checked').each(function() {
            checked_reports.push($(this)[0].dataset['recordId']);
        });
        if(checked_reports.length == 0){
            return true;
        }
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/ohada_reports',
            data: {"model": "ohada.financial.html.report",
                   "options": JSON.stringify(self.data['options']),
                   "output_format": "pdf_bundle",
                   "financial_id": 1,
                   "bundle_items": checked_reports},
            success: def.resolve.bind(def),
            error: function () {
                crash_manager.rpc_error.apply(crash_manager, arguments);
                def.reject();
            },
            complete: framework.unblockUI,
        });
        return def;
    },

    _updateTemplateBody: function () {
        this.$el.empty();
        this.$el.append(core.qweb.render('ManagerDashboard', {widget: this}));
        this.render_graphs();
        document.getElementById("myForm").style.display = "none";
        this.update_cp();
        this.render_searchview_buttons();
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['ManagerDashboard'];
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
            self.update_cp();
            self.$searchview_buttons = $(self.data['search_panel']);
            self.render_searchview_buttons();
        });
    },

    render_dashboards: function() {
        var self = this;
        if (this.data){
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_ohada_dashboard').append(QWeb.render(template, {widget: self}));
            });
            }
        else{
            self.$('.o_ohada_dashboard').append(QWeb.render('OhadaWarning', {widget: self}));
            }
    },

    render_graphs: function(){
        var self = this;
        if (this.data){
            self.render_leave_graph();
            self.render_leave_graph2();
            self.update_join_resign_trends();
        }
    },

    update_join_resign_trends: function(){
        var self = this;
        var data = [
            {
                key: "Cashflow",
                color: "#acacbf",           //999494    acacbf      c0c0cc
                area: true,
                values: [
                    {y: self.data['di_data']['CF'][0]['count'], name: self.data['di_data']['CF'][0]['l_month'], x: self.data['di_data']['CF'][0]['l_month'], label: self.data['di_data']['CF'][0]['l_month']},
                    {y: self.data['di_data']['CF'][1]['count'], name: self.data['di_data']['CF'][1]['l_month'], x: self.data['di_data']['CF'][1]['l_month'], label: self.data['di_data']['CF'][1]['l_month']},
                    {y: self.data['di_data']['CF'][2]['count'], name: self.data['di_data']['CF'][2]['l_month'], x: self.data['di_data']['CF'][2]['l_month'], label: self.data['di_data']['CF'][2]['l_month']},
                    {y: self.data['di_data']['CF'][3]['count'], name: self.data['di_data']['CF'][3]['l_month'], x: self.data['di_data']['CF'][3]['l_month'], label: self.data['di_data']['CF'][3]['l_month']},
                ]
            }
        ];
        nv.addGraph(function() {
            var chart = nv.models.lineChart();
            chart.forceY([0]);
            chart.options({
                x: function (d, u) { return u; },
                margin: {'left': 14, 'right': 14, 'top': 20, 'bottom': 17},
                showYAxis: false,
                showLegend: false,
            });
            chart.xAxis.tickFormat(function (d) {
                var label = '';
                _.each(data, function (v){
                    if (v.values[d] && v.values[d].x){
                        label = v.values[d].x;
                    }
                });
                return label;
            });
            chart.yAxis.tickFormat(d3.format(',.0f'));
            chart.xAxis.axisLabel(data[0].name);

            d3.select('#chart3')
                .datum(data)
                .transition().duration(600)
                .call(chart);
        //    nv.utils.windowResize(function() { chart.update() });
            return chart;
        });
    },


    render_leave_graph2:function(){
        var self = this;
        var data = [
            {
              key: "",
              values: [
                {value: self.data['di_data']['PL'][0][1], label: self.data['di_data']['PL'][0][0]},
                {value: self.data['di_data']['PL'][1][1], label: self.data['di_data']['PL'][1][0]},
                {value: self.data['di_data']['PL'][2][1], label: self.data['di_data']['PL'][2][0]},
                {value: self.data['di_data']['PL'][3][1], label: self.data['di_data']['PL'][3][0]},
              ]
            }
        ];
        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function (d) { return d.label; })
                .y(function (d) { return d.value; })
                .showValues(false)
                .showYAxis(false)
                .color(['#acacbf'])
                .margin({'left': 15, 'right': 15, 'top': 20, 'bottom': 12});

            chart.xAxis.axisLabel(data[0].title);
            chart.yAxis.tickFormat(d3.format(',.0f'));

            d3.select('#chart2')
                .datum(data)
                .transition().duration(600)
                .call(chart);
        //    nv.utils.windowResize(function() { chart.update() });
            return chart;
        });
    },

    render_leave_graph:function(){
        var self = this;
        var data = [
            {
              key: "",
              values: [
                {value: self.data['di_data']['BS'][0][1], label: self.data['di_data']['BS'][0][0]},
                {value: self.data['di_data']['BS'][1][1], label: self.data['di_data']['BS'][1][0]},
                {value: self.data['di_data']['BS'][2][1], label: self.data['di_data']['BS'][2][0]},
                {value: self.data['di_data']['BS'][3][1], label: self.data['di_data']['BS'][3][0]},
              ]
            }
        ];
        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function (d) { return d.label; })
                .y(function (d) { return d.value; })
                .showValues(false)
                .showYAxis(false)
                .color(['#acacbf'])
                .margin({'left': 0, 'right': 0, 'top': 20, 'bottom': 12});

            chart.xAxis.axisLabel(data[0].title);
            chart.yAxis.tickFormat(d3.format(',.0f'));

            d3.select('#chart')
                .datum(data)
                .transition().duration(600)
                .call(chart);
        //    nv.utils.windowResize(function() { chart.update() });
            return chart;
        });
    },

    render_searchview_buttons: function() {
        var self = this;
        // bind searchview buttons/filter to the correct actions

        $('.js_account_report_choice_year').click(function(e){
            self.fetch_data(parseInt(e['currentTarget'].getAttribute('value')), self.data['options']['all_entries']).then(function() {
                self._updateTemplateBody();
            });
        });

        $('.js_account_report_choice_entries').click(function(e){
            var entries_value = (e['currentTarget'].getAttribute('value') == 'True');
            self.fetch_data(self.data['this_year'], entries_value).then(function() {
                self._updateTemplateBody();
            });
        });

    },


});


core.action_registry.add('ohada_dashboard', OhadaDashboard);

return OhadaDashboard;

});