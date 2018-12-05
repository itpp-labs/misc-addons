odoo.define('project_task_subtask.one2many_renderer', function(require){

    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var BasicModel = require('web.BasicModel');

    FieldOne2Many.include({

        check_task_tree_mode: function(){
            if (this.view &&
            this.view.arch.tag === 'tree' &&
            this.record && this.record.model === "project.task"
            ) {
                return true;
            }
            return false;
        },

        sort_data: function() {
            var user_id = this.record.context.uid;

            var new_rows = _.filter(this.value.data, function(d){
                return !d.res_id;
            });
            var data = _.difference(this.value.data, new_rows);

            _.each(data, function(d){
                d.u_name = d.data.user_id.data.display_name;
            });

            var name_index = _.sortBy(_.uniq(_.map(data, function(d){
                return d.data.user_id.data.display_name;
            })));


            data = _.sortBy(data, 'u_name');
            _.each(data, function(d){
                d.deadline = d.data.deadline;
                if (d.data.user_id.data.id === user_id) {
                    d.index = 0;
                } else {
                    d.index = (_.indexOf(name_index, d.data.user_id.data.display_name) + 1) * 1000000;
                }
            });

            data = _.sortBy(data, 'deadline');
            _.each(data, function(d){
                d.index += _.indexOf(data, d);
                if (!d.deadline) {
                    d.index += 90000;
                }
                if (d.data.state === 'todo') {
                    // continue
                } else if (d.data.state === 'waiting') {
                    d.index += 100000;
                } else if (d.data.state === 'done') {
                    d.index += 400000;
                } else {
                    d.index += 700000;
                }
            });
            data = _.sortBy(data, 'index');
            _.each(new_rows, function(r){
                data.push(r);
            });
            this.value.data = data;
        },

        _render: function () {
            if (this.check_task_tree_mode()) {
                this.sort_data();
            }
            return this._super(arguments);
        },

        reset: function (record, ev, fieldChanged) {
            var self = this;
            return this._super.apply(this, arguments).then(function(res){
                if (self.check_task_tree_mode()) {
                    self._render();
                }
            });
        },

    });

    BasicModel.include({

        _sortList: function(list){
            // taken from odoo
            if (!list.static) {
                // only sort x2many lists
                return;
            }
            var self = this;
            // -----

            if (list.model === "project.task.subtask" && list.orderedResIDs) {
                var rows = [];
                var new_rows = [];
                _.each(list.data, function(d){
                    var r = self.localData[d];
                    if (Number(r.res_id) === r.res_id) {
                        rows.push(r);
                    } else {
                        new_rows.push(r);
                    }
                });
                rows = this.sort_data(rows, list.context.uid, this);
                _.each(new_rows, function(r){
                    rows.push(r);
                });
                list.orderedResIDs = _.pluck(rows, 'res_id');
                return this._setDataInRange(list);
            }

            return this._super(list);

        },

        sort_data: function(data, user_id, parent) {
            user_id = user_id || 1;

            _.each(data, function(d){
                d.u_name = parent.localData[d.data.user_id].data.display_name;
            });

            var name_index = _.sortBy(_.uniq(_.map(data, function(d){
                return parent.localData[d.data.user_id].data.display_name;
            })));


            data = _.sortBy(data, 'u_name');
            _.each(data, function(d){
                d.deadline = d.data.deadline;
                if (parent.localData[d.data.user_id].data.id === user_id) {
                    d.index = 0;
                } else {
                    d.index = (_.indexOf(name_index, parent.localData[d.data.user_id].data.display_name) + 1) * 1000000;
                }
            });

            data = _.sortBy(data, 'deadline');
            _.each(data, function(d){
                d.index += _.indexOf(data, d);
                if (!d.deadline) {
                    d.index += 90000;
                }
                if (d.data.state === 'todo') {
                    // continue
                } else if (d.data.state === 'waiting') {
                    d.index += 100000;
                } else if (d.data.state === 'done') {
                    d.index += 400000;
                } else {
                    d.index += 700000;
                }
            });
            return _.sortBy(data, 'index');
        },

    });
});
