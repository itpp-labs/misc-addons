openerp.project_timelog = function(openerp) {
    openerp.web.FormView.include({
        load_form: function(data) {
            console.log("test");
            //if (this.view.dataset.model === 'project.task.work') {
            //td[data-field='play_timer']
                $("button").click(function(){
                    console.log('ok2');
                });
            //}
            this._super(data);
    }
        //load_form: function(data) {
        //    this._super(field_manager, node);
        //    if (this.view.dataset.model === 'project.task.work') {
        //        $("span[class='oe_form_char_content']").click(function(e){
        //            console.log('ok2');
        //            console.log(e.target.tagName)
        //        })
        //    }
        //}
    });
};