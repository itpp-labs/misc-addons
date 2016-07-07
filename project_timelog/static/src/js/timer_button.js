openerp.project_timelog = function(openerp) {
    var reload_page = true;
    openerp.web.form.FormWidget.include({
        init: function(field_manager, node) {
            this._super(field_manager, node);

            if (this.view.dataset.model === 'project.task.work') {
                if (this.view.dataset.parent_view!=undefined && reload_page) {
                    console.log(this.view.dataset.parent_view.datarecord.id);
                    reload_page = false;
                }
            }
        }
    });
};