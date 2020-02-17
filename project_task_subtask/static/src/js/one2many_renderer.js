/*  Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("project_task_subtask.one2many_renderer", function(require) {
    "use strict";
    var FieldOne2Many = require("web.relational_fields").FieldOne2Many;
    var BasicModel = require("web.BasicModel");

    var core = require("web.core");
    var QWeb = core.qweb;

    FieldOne2Many.include({
        check_task_tree_mode: function() {
            if (
                this.view &&
                this.view.arch.tag === "tree" &&
                this.record &&
                this.record.model === "project.task" &&
                this.name === "subtask_ids"
            ) {
                return true;
            }
            return false;
        },

        sort_data: function() {
            var user_id = this.record.context.uid;

            var new_rows = _.filter(this.value.data, function(d) {
                return !d.res_id;
            });
            var data = _.difference(this.value.data, new_rows);

            _.each(data, function(d) {
                d.u_name = d.data.user_id.data.display_name;
            });

            var name_index = _.sortBy(
                _.uniq(
                    _.map(data, function(d) {
                        return d.data.user_id.data.display_name;
                    })
                )
            );

            data = _.sortBy(data, "u_name");
            _.each(data, function(d) {
                d.deadline = d.data.deadline;
                if (d.data.user_id.data.id === user_id) {
                    d.index = 0;
                } else {
                    d.index =
                        (_.indexOf(name_index, d.data.user_id.data.display_name) + 1) *
                        1000000;
                }
            });

            data = _.sortBy(data, "deadline");
            _.each(data, function(d) {
                d.index += _.indexOf(data, d);
                if (!d.deadline) {
                    d.index += 90000;
                }
                if (d.data.state === "todo") {
                    // Continue
                } else if (d.data.state === "waiting") {
                    d.index += 100000;
                } else if (d.data.state === "done") {
                    d.index += 400000;
                } else {
                    // Makes cancelled subtasks stay last in line
                    d.index += (name_index.length + 2) * 1000000;
                    if (d.data.user_id.data.id !== user_id) {
                        d.index +=
                            (_.indexOf(name_index, d.data.user_id.data.display_name) +
                                1) *
                            1000000;
                    }
                }
            });
            data = _.sortBy(data, "index");
            _.each(new_rows, function(r) {
                data.push(r);
            });
            this.default_sorting = this.value.data;
            this.value.data = data;
        },

        _render: function() {
            if (this.check_task_tree_mode() && this.getParent().list_is_sorted) {
                this.sort_data();
            }
            return this._super(arguments);
        },

        reset: function(record, ev, fieldChanged) {
            var self = this;
            return this._super.apply(this, arguments).then(function(res) {
                if (self.check_task_tree_mode() && self.getParent().list_is_sorted) {
                    self._render();
                }
            });
        },

        _renderControlPanel: function() {
            var self = this;
            if (this.check_task_tree_mode()) {
                if (!this.$buttons) {
                    this.$buttons = $("<div/>");
                }
                this.$buttons[0].innerHTML += QWeb.render("SubtaskSortButtons", {});
                return this._super(arguments).done(function(res) {
                    self._update_custom_sort_buttons();
                });
            }
            return this._super(arguments);
        },

        _update_custom_sort_buttons: function() {
            var self = this;
            var sort_button = this.$el.find(".o_pager_sort");
            var unsort_button = this.$el.find(".o_pager_unsort");

            var sorting = this.getParent().list_is_sorted || false;

            if (sorting) {
                sort_button.hide();
            } else {
                unsort_button.hide();
            }
            this.default_sorting = this.value.data;

            sort_button.off().on("click", function(e) {
                self.getParent().list_is_sorted = true;
                sort_button.hide();
                unsort_button.show();
                self._render();
            });
            unsort_button.off().on("click", function(e) {
                self.getParent().list_is_sorted = false;
                sort_button.show();
                unsort_button.hide();
                self.value.data = self.default_sorting;
                self._render();
            });
        },
    });

    BasicModel.include({
        _sortList: function(list) {
            // Taken from odoo
            if (!list.static) {
                // Only sort x2many lists
                return;
            }
            var self = this;
            // -----

            if (list.model === "project.task.subtask" && list.orderedResIDs) {
                var rows = [];
                var new_rows = [];
                _.each(list.data, function(d) {
                    var r = self.localData[d];
                    if (Number(r.res_id) === r.res_id) {
                        rows.push(r);
                    } else {
                        new_rows.push(r);
                    }
                });
                rows = this.sort_data(rows, list.context.uid, this);
                _.each(new_rows, function(r) {
                    rows.push(r);
                });
                list.orderedResIDs = _.pluck(rows, "res_id");
                return this._setDataInRange(list);
            }

            return this._super(list);
        },

        sort_data: function(data, user_id, parent) {
            user_id = user_id || 1;

            _.each(data, function(d) {
                d.u_name = parent.localData[d.data.user_id].data.display_name;
            });

            var name_index = _.sortBy(
                _.uniq(
                    _.map(data, function(d) {
                        return parent.localData[d.data.user_id].data.display_name;
                    })
                )
            );

            data = _.sortBy(data, "u_name");
            _.each(data, function(d) {
                d.deadline = d.data.deadline;
                if (parent.localData[d.data.user_id].data.id === user_id) {
                    d.index = 0;
                } else {
                    d.index =
                        (_.indexOf(
                            name_index,
                            parent.localData[d.data.user_id].data.display_name
                        ) +
                            1) *
                        1000000;
                }
            });

            data = _.sortBy(data, "deadline");
            _.each(data, function(d) {
                d.index += _.indexOf(data, d);
                if (!d.deadline) {
                    d.index += 90000;
                }
                if (d.data.state === "todo") {
                    // Continue
                } else if (d.data.state === "waiting") {
                    d.index += 100000;
                } else if (d.data.state === "done") {
                    d.index += 400000;
                } else {
                    d.index += 700000;
                }
            });
            return _.sortBy(data, "index");
        },
    });
});
