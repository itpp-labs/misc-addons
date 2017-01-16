openerp.gamification_extra = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    instance.gamification.Sidebar.include({
        init: function(){
            this._super.apply(this, arguments);
            var self = this;
            this.events['click .oe_goal_details'] = function(event){
                var $t = $(event.currentTarget);
                self.do_action({
                    'name': _t('Details'),
                    'type': 'ir.actions.act_window',
                    'res_model': $t.attr('data-model'),
                    'target': 'current',
                    'views': [[false, 'list'], [false, 'form']],
                    'domain':  $t.attr('data-domain'),
                });
            };
        },
    });
};
