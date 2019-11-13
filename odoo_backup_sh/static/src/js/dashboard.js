// Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
// Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
// Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
odoo.define('odoo_backup_sh.dashboard', function (require) {
'use strict';

// see https://eslint.org/docs/rules/no-undef
/*global moment, Chart*/
var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var time = require('web.time');
var field_utils = require('web.field_utils');
var QWeb = core.qweb;
var _t = core._t;

function DATE_FORMAT(){
    return time.getLangDateFormat();
}
function LANG_CODE(){
    return _t.database.parameters.code;
}
var COLORS = ["#1f77b4", "#aec7e8"];
var FORMAT_OPTIONS = {
    // allow to decide if utils.human_number should be used
    humanReadable: function (value) {
        return Math.abs(value) >= 1000;
    },
    // with the choices below, 1236 is represented by 1.24k
    minDigits: 1,
    decimals: 2,
    // avoid comma separators for thousands in numbers when human_number is used
    formatterCallback: function (str) {
        return str;
    },
};

var Dashboard = AbstractAction.extend({
    hasControlPanel: false,
    contentTemplate: 'odoo_backup_sh.BackupDashboardMain',
    jsLibs: [
        '/web/static/lib/Chart/Chart.js',
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
            }).then(function(results) {
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
    on_attach_callback: function () {
        this._isInDom = true;
        this.render_graphs();
        this._super.apply(this, arguments);
    },
    on_detach_callback: function () {
        this._isInDom = false;
        this._super.apply(this, arguments);
    },
    render_graphs: function(){
        if (!this.show_nocontent_msg) {
            this.render_remote_storage_usage_graph();
        }
        this.render_backup_config_cards();
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
        return this.service || 'total';
    },
    formatValue: function (value) {
        var formatter = field_utils.format.float;
        var formatedValue = formatter(value, null, FORMAT_OPTIONS);
        return formatedValue;
    },
    capitalize: function (value){
        return value.charAt(0).toUpperCase() + value.slice(1);
    },
    render_remote_storage_usage_graph: function(chart_values) {
        var chart_id = 'odoo_backup_sh-chart-total-usage';
        this.$('#graph_remote_storage_usage').empty();
        this.$('h2[class="graph_title"]').text(_t(this.get_service() + ' remote storage usage'));
        chart_values = chart_values || this.remote_storage_usage_graph_values;
        var self = this;

        var $canvasContainer = $('<div/>', {class: 'o_graph_canvas_container'});
        this.$canvas = $('<canvas/>').attr('id', chart_id);
        $canvasContainer.append(this.$canvas);
        this.$('#graph_remote_storage_usage').append($canvasContainer);

        var labels = chart_values[0].values.map(function (date) {
            return moment(date[0], "YYYY-MM-DD", 'en');
            //return moment(date[0], "MM/DD/YYYY", 'en');
        });

        var datasets = chart_values.map(function (group, index) {
            return {
                label: group.key,
                data: group.values.map(function (value) {
                    return value[1];
                }),
                dates: group.values.map(function (value) {
                    return value[0];
                }),
                fill: false,
                borderColor: COLORS[index],
            };
        });

        var ctx = document.getElementById(chart_id);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                legend: {
                    display: false,
                },
                maintainAspectRatio: false,
                scales: {
                    yAxes: [{
                        type: 'linear',
                        ticks: {
                            beginAtZero: true,
                            callback: this.formatValue.bind(this),
                        },
                        scaleLabel: {
                            display: true,
                            labelString: _t('Usage Value, MB'),
                        }
                    }],
                    xAxes: [{
                        ticks: {
                            callback: function (moment) {
                                return moment.format(DATE_FORMAT());
                            },
                        }
                    }],
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                    bodyFontColor: 'rgba(0,0,0,1)',
                    titleFontSize: 13,
                    titleFontColor: 'rgba(0,0,0,1)',
                    backgroundColor: 'rgba(255,255,255,0.6)',
                    borderColor: 'rgba(0,0,0,0.2)',
                    borderWidth: 2,
                    callbacks: {
                        title: function (tooltipItems, data) {
                            return data.datasets[0].label;
                        },
                        label: function (tooltipItem, data) {
                            var moment = data.labels[tooltipItem.index];
                            var date = tooltipItem.datasetIndex === 0 ? moment
                                : moment.subtract(1, self.date_range);
                            return date.format(DATE_FORMAT()) + ': ' + self.formatValue(tooltipItem.yLabel);
                        },
                        labelColor: function (tooltipItem, chart) {
                            var dataset = chart.data.datasets[tooltipItem.datasetIndex];
                            return {
                                borderColor: dataset.borderColor,
                                backgroundColor: dataset.borderColor,
                            };
                        },
                    }
                }
            }
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
        var chart_id = 'odoo_backup_sh-' + service + '-' + db_name;
        var chart_values = this.configs.filter(function (config) {
            return config.database === db_name && config.storage_service === service;
        })[0].graph;
        var self = this;

        var div_to_display = 'div[data-db_name="' + db_name + '"][data-service="' + service + '"] .backup_config_card_graph';

        this.$(div_to_display).empty();
        var $canvasContainer = $('<div/>', {class: 'o_graph_canvas_container'});
        this.$canvas = $('<canvas/>').attr('id', chart_id);
        $canvasContainer.append(this.$canvas);
        this.$(div_to_display).append($canvasContainer);

        var labels = chart_values[0].values.map(function (date) {
            return moment(date.label, "YYYY-MM-DD", 'en');
        });

        // var color = 'rgb(124, 123, 173)';
        var color = COLORS[1];
        var datasets = chart_values.map(function (group, index) {
            return {
                label: group.key,
                data: group.values.map(function (value) {
                    return value.value;
                }),
                dates: group.values.map(function (value) {
                    return value.label;
                }),
                fill: false,
                borderColor: color,
                backgroundColor: color
            };
        });

        console.log(_t.database.parameters);
        var ctx = document.getElementById(chart_id);
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                legend: {
                    display: false,
                },
                maintainAspectRatio: false,
                scales: {
                    yAxes: [{
                        type: 'linear',
                        ticks: {
                            beginAtZero: true,
                            callback: this.formatValue.bind(this),
                        },
                    }],
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: _t('Backups of the Last 7 Days')
                        },
                        ticks: {
                            callback: function (moment) {
                                // capitalize for non-english locales like russian
                                return self.capitalize(moment.locale((LANG_CODE())).format('dddd'));
                            },
                        }
                    }],
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                    bodyFontColor: 'rgba(0,0,0,1)',
                    titleFontSize: 13,
                    titleFontColor: 'rgba(0,0,0,1)',
                    backgroundColor: 'rgba(255,255,255,0.6)',
                    borderColor: 'rgba(0,0,0,0.2)',
                    borderWidth: 2,
                    callbacks: {
                        title: function (tooltipItems, data) {
                            return data.datasets[0].label;
                        },
                        label: function (tooltipItem, data) {
                            var moment = data.labels[tooltipItem.index];
                            var date = tooltipItem.datasetIndex === 0 ? moment
                                : moment.subtract(1, self.date_range);
                            return date.format(DATE_FORMAT()) + ': ' + self.formatValue(tooltipItem.yLabel);
                        },
                        labelColor: function (tooltipItem, chart) {
                            var dataset = chart.data.datasets[tooltipItem.datasetIndex];
                            return {
                                borderColor: dataset.borderColor,
                                backgroundColor: dataset.borderColor,
                            };
                        },
                    }
                }
            }
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
