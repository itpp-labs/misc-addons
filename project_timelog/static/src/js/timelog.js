$(document).ready(function() {
    "use strict";
    var TimeLog = openerp.TimeLog = {};

    TimeLog.Manager = openerp.Widget.extend({
        init: function () {
            this._super();
            var self = this;
            //var bus_last = 0;
            //Number(storage.getItem("bus_last"))==null ? bus_last=this.bus.last : bus_last=Number(storage.getItem("bus_last"));

            // start the polling
            this.bus = openerp.bus.bus;
            //this.bus.last = bus_last;
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
        },
        on_notification: function (notification) {
            var self = this;
            console.log('notification');
            if (typeof notification[0][0] === 'string') {
                notification = [notification]
            }
            for (var i = 0; i < notification.length; i++) {
                var channel = notification[i][0];
                var message = notification[i][1];
                this.on_notification_do(channel, message);
            }
        },
        on_notification_do: function (channel, message) {
            console.log("on_notification_do");
            var self = this;
            var channel = JSON.parse(channel);
            var error = false;
            if (Array.isArray(channel) && channel[1] === 'project.timelog') {
                try {
                    this.received_message(message);
                } catch (err) {
                    error = err;
                    console.error(err);
                }
            }
        },
        received_message: function(message) {
            console.log(message);
            //отображение сообщения
        }

    });

    TimeLog.Conversation = openerp.Widget.extend({
        init: function(){
            this._super();
            var self = this;
            openerp.session = new openerp.Session();
            this.c_manager = new openerp.TimeLog.Manager();
            console.log("Initial timer");
            this.start();
        },
        start: function(){
            var self = this;
            openerp.session.rpc("/timelog/init", {}).then(function(notification){
               console.log(notification);
            });
        }
    });
    var new_time_log = new TimeLog.Conversation(this);

});