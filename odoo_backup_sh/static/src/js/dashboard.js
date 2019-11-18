// Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
// Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

odoo.define('odoo_backup_sh.dashboard', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

var Dashboard = AbstractAction.extend(ControlPanelMixin, {
    template: 'odoo_backup_sh.BackupDashboardMain',
    need_control_panel: false,
    cssLibs: [
        '/web/static/lib/nvd3/nv.d3.css'
    ],
    jsLibs: [
        '/web/static/lib/nvd3/d3.v3.js',
        '/web/static/lib/nvd3/nv.d3.js',
        '/web/static/src/js/libs/nvd3.js'
    ],
    events: {
        'click .o_dashboard_action': 'on_dashboard_action',
        'click .o_dashboard_get_s3_credentials': 'o_dashboard_get_s3_credentials',
        'click .o_dashboard_action_add_database': 'o_dashboard_action_add_database',
        'click .o_dashboard_action_update_info': 'o_dashboard_action_update_info',
        'click .o_dashboard_action_make_backup': 'o_dashboard_action_make_backup',
        'click .o_dashboard_action_backup_config': 'o_dashboard_action_backup_config',
        'click .o_dashboard_action_view_backups': 'o_dashboard_action_view_backups',
        'click .o_backup_dashboard_notification .close': 'close_dashboard_notification',
        'click .kanban_group_buttons .btn': 'click_group_buttons',
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_dashboard_data();
        });
    },

    fetch_dashboard_data: function() {
        var self = this;
        return self._rpc({
                route: '/odoo_backup_sh/fetch_dashboard_data',
            }).done(function(results) {
                self.remote_storage_usage_graph_values = results.remote_storage_usage_graph_values;
                self.services_storage_usage_graph_values = results.services_storage_usage_graph_values;
                self.configs = results.configs;
                self.notifications = results.notifications;
                self.up_balance_url = results.up_balance_url;
                self.show_nocontent_msg = results.configs.length === 0;
                self._msg = results.configs.length === 0;
                self.modules = results.modules;
                self.cloud_params = results.cloud_params;
            });
    },
    on_dashboard_action: function (ev) {
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        this.do_action($action.attr('name'));
    },

    dashboard_can_backup: function(){
        return this.modules.odoo_backup_sh.configured ||
            this.modules.odoo_backup_sh_dropbox.configured ||
            this.modules.odoo_backup_sh_google_disk.configured;
    },
    dashboard_basic: function(){
        return !this.modules.odoo_backup_sh.configured &&
            !this.modules.odoo_backup_sh_dropbox.installed &&
            !this.modules.odoo_backup_sh_google_disk.installed;
    },
    dashboard_configure_dropbox: function(){
        return this.modules.odoo_backup_sh_dropbox.installed &&
            !this.modules.odoo_backup_sh_dropbox.configured;
    },
    dashboard_configure_google_disk: function(){
        return this.modules.odoo_backup_sh_google_disk.installed &&
            !this.modules.odoo_backup_sh_google_disk.configured;
    },
    dashboard_offer_iap: function(){
        return (this.modules.odoo_backup_sh_dropbox.configured ||
                this.modules.odoo_backup_sh_google_disk.configured) && !this.modules.odoo_backup_sh.configured;
    },
    dashboard_iap: function(){
        return this.modules.odoo_backup_sh.configured_iap;
    },
    dashboard_offer_extra_module: function(){
        return this.modules.odoo_backup_sh.configured &&
            !this.modules.odoo_backup_sh.configured_iap &&
            !this.modules.odoo_backup_sh_dropbox.installed &&
            !this.modules.odoo_backup_sh_google_disk.installed;
    },
    auth_via_odoo: function(){
        if ('auth_link' in this.cloud_params) {
            self.do_action({
                name: "Auth via odoo.com",
                target: 'self',
                type: 'ir.actions.act_url',
                url: this.cloud_params.auth_link
            });
        }
        /*
        self._rpc({
            model: 'odoo_backup_sh.config',
            method: 'get_cloud_params',
            kwargs: {
                redirect: '/web/backup_redirect?redirect=' + window.location.href,
            },
        }).done(function(cloud_params) {
            if ('auth_link' in cloud_params) {
                self.do_action({
                    name: "Auth via odoo.com",
                    target: 'self',
                    type: 'ir.actions.act_url',
                    url: cloud_params.auth_link
                });
            }
            self.cloud_params = cloud_params;
        })*/

    },
    start: function() {
        var self = this;
        return this._super().then(function() {
            self.set_service('total');
            if (!self.show_nocontent_msg) {
                self.render_remote_storage_usage_graph();
            }
            self.render_backup_config_cards();
        });
    },

    set_active_button: function($el) {
        $el.parent().find('.btn-primary').removeClass('btn-primary').addClass('btn-secondary');
        $el.removeClass('btn-secondary');
        $el.addClass('btn-primary');
    },

    click_group_buttons: function(e) {
        e.preventDefault();
        var $el = $(e.target);
        var service = $el.data('service');
        this.set_service(service);
        if (service === 'odoo_backup_sh') {
            this.render_remote_storage_usage_graph(this.services_storage_usage_graph_values[service]);
        } else {
            this.render_remote_storage_usage_graph();
        }
        this.set_active_button($el);
    },

    set_service: function(service) {
        this.service = service;
    },

    get_service: function() {
        return this.service;
    },

    render_remote_storage_usage_graph: function(chart_values) {
        this.$('#graph_remote_storage_usage').empty();
        var service = this.get_service();
        var title;
        if (service === 'total'){
            title = _t('total remote storage usage');
        } else {
            if (service === 'odoo_backup_sh'){
                service = _t('S3');
            } else if (service === 'dropbox'){
                service = _t('Dropbox');
            } else if (service === 'google_drive'){
                service = _t('Google Drive');
            }
            title = _.str.sprintf(_t('%s remote storage usage'), service);
        }

        this.$('h2[class="graph_title"]').text(title);
        chart_values = chart_values || this.remote_storage_usage_graph_values;
        var self = this;

        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                .x(function(d) {
                    return self.getDate(d);
                })
                .y(function(d) {
                    return self.getValue(d);
                })
                .forceY([0])
                .useInteractiveGuideline(true)
                .showLegend(false)
                .showYAxis(true)
                .showXAxis(true);
            var tick_values = self.getPrunedTickValues(chart_values[0].values, 5);

            chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format("%m/%d/%y")(new Date(d));
                })
                .tickValues(_.map(tick_values, function(d) {
                    return self.getDate(d);
                }))
                .rotateLabels(-45);

            chart.yAxis
                .axisLabel('Usage Value, MB')
                .tickFormat(d3.format('.02f'));

            d3.select('#graph_remote_storage_usage')
                .append("svg")
                .attr("height", '24em')
                .datum(chart_values)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    },

    render_backup_config_cards: function() {
        var self = this;
        var $o_backup_dashboard_configs = self.$('.o_backup_dashboard_configs').append(
            QWeb.render('odoo_backup_sh.config_cards', {configs: self.configs}));
        _.each($o_backup_dashboard_configs.find('.o_kanban_record'), function(record) {
            self.render_backup_config_card_graph(record.dataset.db_name, record.dataset.service);
        });
    },

    render_backup_config_card_graph: function(db_name, service) {
        var chart_values = this.configs.filter(function (config) {
            return config.database === db_name && config.storage_service === service;
        })[0].graph;

        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) {
                    return d.label;
                })
                .y(function(d) {
                    return d.value;
                })
                .showValues(true)
                .showYAxis(false)
                .color(['#7c7bad'])
                .margin({'left': 0, 'right': 0, 'top': 10, 'bottom': 42});

            chart.xAxis
                .axisLabel('Backups of Last 7 Days, MB');

            d3.select('div[data-db_name="' + db_name + '"][data-service="' + service + '"] .backup_config_card_graph')
                .append("svg")
                .attr("height", '10em')
                .datum(chart_values)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    },
    o_dashboard_get_s3_credentials: function(ev){
        window.location.href = '/odoo_backup_sh/get_s3_credentials?redirect=' + encodeURIComponent(window.location.href);
    },
    o_dashboard_action_add_database: function (ev) {
        ev.preventDefault();
        this.do_action({
            name: "Create backup configuration",
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, "form"]],
            res_model: 'odoo_backup_sh.config',
            target: 'current',
        },
        {
            clear_breadcrumbs: true,
        });
    },

    o_dashboard_action_update_info: function (ev) {
        if (ev && ev.preventDefault) {
            ev.preventDefault();
        }
        var self = this;
        this._rpc({
            model: 'odoo_backup_sh.config',
            method: 'update_info',
            kwargs: {
                cloud_params: self.cloud_params,
            },
        }).then(function (result) {
            if ('reload_page' in result) {
                window.location.reload();
            }
            $.when(self.fetch_dashboard_data()).then(function() {
                self.$('#graph_remote_storage_usage').empty();
                self.$('.o_backup_dashboard_configs').empty();
                self.start();
            });
        });
    },

    o_dashboard_action_make_backup: function (ev) {
        ev.preventDefault();
        var self = this;
        var service = $(ev.currentTarget).closest('div[data-service]').data('service');
        this._rpc({
            model: 'odoo_backup_sh.config',
            method: 'make_backup',
            kwargs: {
                name: $(ev.currentTarget).closest('div[data-db_name]').data('db_name'),
                service: service,
            },
        }).then(function (result) {
            // always reload to update graphs
            window.location.reload();

            // Commented, because it's not clear why do we need it here. That
            // method applies rotations and checks for missed records, while all should be clean here

            // self.o_dashboard_action_update_info(self.cloud_params);
        });
    },

    o_dashboard_action_view_backups: function (ev) {
        ev.preventDefault();
        this.do_action({
            name: "Backups",
            type: 'ir.actions.act_window',
            views: [[false, 'list'], [false, 'form'], [false, 'graph']],
            res_model: 'odoo_backup_sh.backup_info',
            context: {
                'search_default_group_upload_datetime': 1
            },
            target: 'current',
            domain: [['database', '=', $(ev.currentTarget).closest('div[data-db_name]').data('db_name')],
                ['storage_service', '=', $(ev.currentTarget).closest('div[data-service]').data('service')]],
        },
        {
            clear_breadcrumbs: true,
        });
    },

    o_dashboard_action_backup_config: function (ev) {
        ev.preventDefault();
        this.do_action({
            name: "Backup Configuration",
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            view_mode: 'form',
            res_model: 'odoo_backup_sh.config',
            res_id: $(ev.currentTarget).data('res_id'),
            target: 'current',
        },
        {
            clear_breadcrumbs: true,
        });
    },

    close_dashboard_notification: function (ev) {
        ev.preventDefault();
        var $o_backup_dashboard_notification = $(ev.currentTarget).closest('.o_backup_dashboard_notification');
        this._rpc({
            model: 'odoo_backup_sh.notification',
            method: 'toggle_is_read',
            args: [$o_backup_dashboard_notification.data('notification_id')]
        }).then(function () {
            $o_backup_dashboard_notification.hide();
        });
    },

    // Utility functions
    getDate: function(d) {
        return new Date(d[0]);
    },
    getValue: function(d) {
        return d[1];
    },
    getPrunedTickValues: function(ticks, nb_desired_ticks) {
        var nb_values = ticks.length;
        var keep_one_of = Math.max(1, Math.floor(nb_values / nb_desired_ticks));

        return _.filter(ticks, function(d, i) {
            return i % keep_one_of === 0;
        });
    },
});

core.action_registry.add('backup_dashboard', Dashboard);

return Dashboard;
});
