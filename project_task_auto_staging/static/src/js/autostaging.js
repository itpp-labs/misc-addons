openerp.project_task_auto_staging = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.project_task_auto_staging.Days = instance.web.form.AbstractField.extend({
        render_value: function() {
            var self = this;
            var stageID = this.field_manager.get_field_value("stage_id");
            var model = new instance.web.Model("project.task");
            model.call("get_current_stage", [stageID]).
                  then(function(from_stage) { 
                     var to_stage = self.get("value");
                     var field = from_stage + "->" + to_stage;
                     self.$el.text(field);
                  });
        },
 
    });
    instance.web.form.widgets.add('days', 'instance.project_task_auto_staging.Days');
};
