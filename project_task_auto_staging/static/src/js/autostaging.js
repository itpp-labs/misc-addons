openerp.project_task_auto_staging = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.project_task_auto_staging.Days = instance.web.form.AbstractField.extend({
        render_value: function() {
            var self = this;
            var write_date = this.field_manager.get_field_value("write_date");
            if (!write_date) {
               var model = new instance.web.Model("project.task");
               model.call("get_today", {context: new instance.web.CompoundContext()}).
                  then(function(today) { 
                       self.get_rest_day(today);
                  });
            }
            else {self.get_rest_day(write_date);} 
        },
        get_rest_day: function(wd){
            var self = this;
            var model = new instance.web.Model("project.task");
            model.call("get_rest_day", [wd]).
                then(function(diff) { 
                     var delay = self.field_manager.get_field_value("delay_automove");
                     var rest = delay - diff; 
                     var moved_date = self.get("value");
                     var text = moved_date;
                     if (rest > 0) {text += " (after " + rest + " days)";}
                     self.$el.text(text);
                });
        },
    });
    instance.web.form.widgets.add('autostaging_days', 'instance.project_task_auto_staging.Days');

};
