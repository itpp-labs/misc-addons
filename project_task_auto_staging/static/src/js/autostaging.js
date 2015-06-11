openerp.project_task_auto_staging = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.project_task_auto_staging.Days = instance.web.form.AbstractField.extend({
        start: function() {
            var self = this; 
            this.on("change:random_data", this, this.random_data_changed);
            this.set("random_data", Math.random());
            $("header").click(function (){  self.set("random_data", Math.random());  });
            this._super();
        },
        random_data_changed: function() {
            var self = this; 
            setTimeout(function() { self.render_value(); }, 500);
        },
        render_value: function() {
            var self = this;
            var write_date = this.field_manager.get_field_value("write_date");
            var model = new instance.web.Model("project.task");
            if (write_date) {
               model.call("get_rest_day", [write_date]).
                  then(function(diff) { 
                      var delay = self.field_manager.get_field_value("delay");
                       var rest = delay - diff; 
                       var moved_date = self.get("value");
                       var text = moved_date;
                       if (rest > 0) {text += " (after " + rest + " days)";}
                       self.$el.text(text);
                  });
            }
        },
 
    });
    instance.web.form.widgets.add('days', 'instance.project_task_auto_staging.Days');

};
