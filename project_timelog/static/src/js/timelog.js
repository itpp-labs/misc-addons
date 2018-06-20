$(document).ready(function() {

    "use strict";
    var TimeLog = openerp.TimeLog = {};
    var audio = new Audio();
    var session = openerp.session;
    var _t = openerp.web._t;

    openerp.web.WebClient.include({
        show_application: function() {
            var self = this;
            this.timelog_widget  = new TimeLog.TimelogWidget(self);
            this.timelog_widget.appendTo(this.$el.parents().find('.oe_timelog_placeholder'));
            return this._super();
        },
    });

    TimeLog.Manager = openerp.Widget.extend({
        init: function (widget) {
            this._super();
            var self = this;
            this.stopline_audio_stop = true;
            this.widget = widget;

            this.channel = JSON.stringify([session.db,"project.timelog",String(session.uid)]);
            // start the polling
            this.bus = openerp.bus.bus;
            this.bus.add_channel(this.channel);
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
        },
        on_notification: function (notification) {
            var self = this;
            if (typeof notification[0][0] === 'string') {
                notification = [notification];
            }
            for (var i = 0; i < notification.length; i++) {
                var channel = notification[i][0];
                var message = notification[i][1];
                this.on_notification_do(channel, message);
            }
        },
        on_notification_do: function (channel, message) {
            var self = this;
            var error = false;
            if (typeof channel != "string") {
                return false;
            }
            if (channel != this.channel) {
                return false;
            }
            channel = JSON.parse(channel);
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
            if (message.status === "play") {
                if (message.active_work_id === this.widget.config.work_id) {
                    this.widget.start_timer();
                } else {
                    this.widget.finish_status = false;
                    this.widget.load_timer_data();
                }
                $('#clock0').css('color','white');
            } else if (message.status == "stop") {
                this.widget.end_datetime_status = true;
                this.widget.stop_timer();
                if (!message.play_a_sound && !message.stopline) {
                    this.widget.change_audio("stop");
                }
                if (message.play_a_sound && !this.widget.stopline) {
                    $('#clock0').css('color','rgb(152, 152, 152)');
                } else if (this.widget.stopline) {
                    $('#clock0').css('color','red');
                }
                if (message.stopline) {
                    $('#clock0').css('color','red');
                    if (this.stopline_audio_stop) {
                        this.widget.change_audio("stop");
                    }
                    this.stopline_audio_stop = false;
                }
            } else if (message.status == "stopline") {
                this.check_stopline(message);
            }
        },
        check_stopline: function(message) {
            var now = new Date();
            var year = now.getFullYear();
            var month = now.getMonth();
            var day = now.getDay();
            var minute = now.getMinutes();

            if (year === message.time.year && month === message.time.month && day === message.time.day) {
                if (minute >= message.time.minute) {
                    $('#clock0').css('color','orange');
                    if (this.song_on) {
                        this.widget.change_audio("warning");
                    }
                }
            }
        },
    });

    TimeLog.TimelogWidget = openerp.Widget.extend({
        init: function(parent){
            this._super(parent);
            var self = this;

            if (window.Audio) {
                this.audio = new Audio();
                this.audio_format = this.audio.canPlayType("audio/ogg; codecs=vorbis")
                                    ? ".ogg"
                                    : ".mp3";
                // the error sound
                this.error = new Audio(session.url("/project_timelog/static/src/audio/offline" + this.audio_format));

            }
            this.status = 'stopped';
            // check connection with server
            window.offLineHandler = function(){
                self.ClientOffLine();
            };
            window.onLineHandler = function(){
                self.ClientOnLine();
            };
            this.c_manager = new TimeLog.Manager(this);
            this.load_timer_data();
        },
        ClientOffLine: function() {
            if (this.status === 'running' && window.Audio) {
                this.error.play();
            }
            this.end_datetime_status = true;
            this.stop_timer();
            this.show_warn_message(_t("No internet connection"));
        },
        ClientOnLine: function(){
            this.change_audio('online');
            this.load_timer_data();
            this.show_notify_message(_t("You are online"));
        },
        change_audio: function(name) {
            if (window.Audio) {
                this.audio.src = session.url("/project_timelog/static/src/audio/" + name + this.audio_format) || this.stop_src;
                this.audio.play();
            }
        },
        load_timer_data: function(){
            var self = this;
            this.activate_click();
            session.rpc("/timelog/init").then(function(data){
                self.config = data;
                self.times = [
                    data.init_log_timer,
                    data.init_task_timer,
                    data.init_day_timer,
                    data.init_week_timer
                ];
                self.end_datetime_status = data.end_datetime_status;
                if (data.time_subtasks <= data.init_log_timer) {
                    self.config.init_log_timer = data.time_subtasks;
                    self.finish_status = true;
                }
                self.add_title(data.subtask_name, data.task_name, data.description_second_timer);
                self.updateView();

                if (data.timer_status) {
                    self.start_timer();
                }
            });
        },
        activate_click: function() {
            var self = this;
            $( "#clock0" ).click(function() {
                self.timer_pause();
            });

            $( "#clock1" ).click(function(event) {
                self.go_to(event, 'task');
            });

            $( "#clock2" ).click(function(event) {
                self.go_to(event, 'day');
            });

            $( "#clock3" ).click(function(event) {
                self.go_to(event, 'week');
            });
        },
        add_favicon: function() {
            if (this.status === 'stopped') {
                $('link[type="image/x-icon"]').attr('href', '/project_timelog/static/src/img/favicon_play.ico');
            } else if (this.status === 'running') {
                $('link[type="image/x-icon"]').attr('href', '/project_timelog/static/src/img/favicon_stop.ico');
            }
        },
        updateView: function() {
            if(!$("#timelog_timer").length) {
                return false;
            }
            for (var i = 0; i < 4; i++) {
              this.updateClock(i, this.times[i]);
            }
        },
        updateClock: function(id, time) {
            var element = document.getElementById("clock"+id);
            var formattedTime = this.formatTime(id, time);
            element.innerHTML = formattedTime;

            if (id === 0) {
                this.update_first_timer();
            } else if (id === 1) {
                this.update_second_timer();
            } else if (id === 2) {
                this.update_third_timer();
            } else if (id === 3) {
                this.update_fourth_timer();
            } else {
                return false;
            }
        },
        update_first_timer: function(){
            var color = false;
            if (this.times[0] === this.config.time_warning_subtasks) {
                color = "orange";
                this.change_audio("warning");
            } else if (this.times[0] > this.config.time_warning_subtasks) {
                color = "orange";
            }

            if ( this.times[0] >= this.config.time_subtasks || this.config.stopline){
                color = "red";
                this.addClass(0, "expired");
                this.timerTimeLimited();
            }

            if (!color) {
                if (this.status === 'stopped') {
                    color = "gray";
                } else {
                    color = "white";
                }
            }
            $('#clock0').css('color', color);
        },
        update_second_timer: function(){
            if (this.config.planned_hours === 0) {
                return false;
            }
            if (this.times[1] >= this.config.planned_hours) {
                $('#clock1').css('color','orange');
            }
            if (this.times[1] >= 2*this.config.planned_hours) {
                $('#clock1').css('color','red');
                this.addClass(1, "expired");
            }
        },
        update_third_timer: function(){
            if (this.times[2] >= this.config.normal_time_day){
                $('#clock2').css('color','yellow');
            }
            if (this.times[2] >= this.config.good_time_day) {
                $('#clock2').css('color','#00f900');
            }
        },
        update_fourth_timer: function() {
            if (this.times[3] === this.config.normal_time_week){
                $('#clock3').css('color','#00f900');
                this.change_audio(2);
            } else if (this.times[3] > this.config.normal_time_week){
                $('#clock3').css('color','#00f900');
            }
            if (this.times[3] === this.config.good_time_week) {
                $('#clock3').css('color','rgb(0, 144, 249)');
                this.change_audio(3);
            } else if (this.times[3] >= this.config.good_time_week) {
                $('#clock3').css('color','rgb(0, 144, 249)');
            }
        },
        timerTimeLimited: function() {
            var self = this;
            if (self.finish_status) {
                return false;
            }
            var model = new openerp.web.Model('project.task.work');
            model.call("stop_timer", [self.work_id, true, false]).then(function(){
                self.finish_status = true;
                var element = document.getElementById("clock0");
                self.startAnim(element, 500, 10*500);
                var id = self.config.task_id;
                var parent = self.getParent();
                var action = {
                    res_id: id,
                    res_model: "project.task",
                    views: [[false, 'form']],
                    type: 'ir.actions.act_window',
                    target: 'current',
                    flags: {
                        action_buttons: true,
                    }
                };
                parent.action_manager.do_action(action);
                self.end_datetime_status = true;
                self.stop_timer();
            });
        },
        addClass : function(id, className) {
            var clockClass = "#clock" + id;
            var element = $(clockClass+" "+className);
            if (element.length) {
                $(clockClass).removeClass(className);
            }
            $(clockClass).addClass(className);
        },
        removeClass : function(id, className) {
            var clockClass = "#clock" + id;
            $(clockClass).removeClass(className);
        },
        formatTime : function(id, time) {
            var minutes = Math.floor(time / 60);
            var seconds = Math.floor(time % 60);
            var hours = Math.floor(minutes / 60);
            minutes = Math.floor(minutes % 60);

            var result = "";
            if (hours < 10) {
                result +="0";
            }
            result += hours + ":";
            if (minutes < 10) {
                result += "0";
            }
            if (id === 0) {
                result += minutes;
                result += "<span id='clock_second'>:";
                if (seconds < 10) {
                    result += "0";
                }
                result +=seconds + "</span>";
            } else {
                result += minutes;
            }
            return result;
        },
        setIntervalTimer: function() {
            var self = this;
            this.timer = window.setInterval(function(){
                self.countDownTimer();
            }, 1000);
        },
        countDownTimer: function() {
            for (var i = 0; i < 4; i++) {
              this.times[i]++;
              this.updateClock(i, this.times[i]);
            }
        },
        start_timer: function(){
            if (this.config.status === 'running' || this.config.time_subtasks <= this.times[0] || this.config.stopline) {
                return false;
            }
            this.add_favicon();
            this.status = 'running';
            this.setIntervalTimer();
            for (var i = 0; i < 4; i++) {
              this.addClass(i, "running");
            }
        },
        stop_timer: function(){
            if (this.status === 'stopped' && this.end_datetime_status){
                return false;
            }
            this.add_favicon();
            this.status = 'stopped';
            for (var i = 0; i < 4; i++) {
                this.removeClass(i, "running");
            }
            clearTimeout(this.timer);
        },
        startAnim: function (element, interval, time) {
            var self = this;
            self.change_audio("stop");
            element.animTimer = setInterval(function () {
                if (element.style.display === "none") {
                    element.style.display = "";
                } else {
                    element.style.display = "none";
                }
            }, interval);
            setTimeout(function(){
                self.stopAnim(element);
            }, time);
        },
        stopAnim: function(element){
            clearInterval(element.animTimer);
            element.style.display = "";
        },
        add_title: function(timer_name, task_name, description) {
            var tws = this.formatTime(1, this.config.time_warning_subtasks).split(':');
            var ts = this.formatTime(1, this.config.time_subtasks).split(':');
            var ntd = this.formatTime(1, this.config.normal_time_day).split(':');
            var gtd = this.formatTime(1, this.config.good_time_day).split(':');
            var ntw = this.formatTime(1, this.config.normal_time_week).split(':');
            var gtw = this.formatTime(1, this.config.good_time_week).split(':');

            $('#clock0').attr("title", 'Subtask: '+timer_name+'\n\nTotal time of the subtask.\n\n* White: time is less than '+ tws[0] +' hours '+tws[1]+' minutes;\n* Short Signal: time is '+ tws[0] +' hours '+tws[1]+' minutes;\n* Yellow: time between '+ tws[0] +' hours '+tws[1]+' minutes and '+ ts[0] +' hours '+ts[1]+' minutes;\n* Long Signal: timer is stopping.\n* Red: timer is stopped;\n\nClick to Play/Pause.');
            $('#clock1').attr("title", 'Task: '+task_name+'\n\nTotal time for the task (includes logs of other users): '+description+"\n\n* White: time is less than 'initially planned hours';\n* Yellow: time is more than 'initially planned hours';\n* Red: time is twice more than 'initially planned hours';\n\nClick to open the task.");
            $('#clock2').attr("title", "Total time of the day.\n\n* White: time is less "+ ntd[0] +" hours "+ntd[1]+" minutes;\n* Yellow: time between "+ ntd[0] +" hours "+ntd[1]+" minutes and "+ gtd[0] +" hours "+gtd[1]+" minutes;\n* Green: time is more than "+ gtd[0] +" hours "+gtd[1]+" minutes;\n\nClick to open logs of the day.");
            $('#clock3').attr("title", "Total time of the week.\n\n* White: time is less than "+ ntw[0] +" hours "+ntw[1]+" minutes\n* Melody #1: time is "+ ntw[0] +" hours "+ntw[1]+" minutes;\n* Yellow: time between "+ ntw[0] +" hours "+ntw[1]+" minutes and "+ gtw[0] +" hours "+gtw[1]+" minutes;\n* Melody #2: time is "+ gtw[0] +" hours "+gtw[1]+" minutes;\n* Blue: time is more than "+ gtw[0] +" hours "+gtw[1]+" minutes;\n\nClick to open logs of the week.");
        },
        timer_pause: function() {
            if (this.finish_status) {
                return false;
            }
            var model_subtask = new openerp.web.Model('project.task.work');
            if (this.status === "running") {
                model_subtask.call("stop_timer", [this.config.work_id]);
                $('#clock0').css('color','gray');
            } else if (this.status === "stopped") {
                model_subtask.call("play_timer", [this.config.work_id]);
                $('#clock0').css('color','white');
            }
        },
        go_to: function(event, status) {
            var id = this.config.task_id;
            var parent = this.getParent();
            var action = false;
            var context = false;
            if (status === 'task') {
                action = {
                    res_id: id,
                    res_model: "project.task",
                    views: [[false, 'form']],
                    type: 'ir.actions.act_window',
                    target: 'current',
                    flags: {
                        action_buttons: true,
                    }
                };
            } else if (status === 'day') {
                context = {
                    'search_default_today': 1,
                    'search_default_group_tasks': 1,
                    'search_default_group_subtasks': 1,
                };
            } else {
                context = {
                    'search_default_group_tasks': 1,
                    'search_default_group_subtasks': 1,
                };
                if (this.config.first_weekday === 'sunday') {
                    context.search_default_week_sunday = 1;
                } else {
                    context.search_default_week = 1;
                }
            }
            if (!action) {
                action = {
                    res_model: "project.timelog",
                    name: "My Timelog",
                    views: [[false, 'list'], [false, 'form']],
                    type: 'ir.actions.act_window',
                    domain: "[('user_id', '=', uid)]",
                    target: 'current',
                    view_mode: 'tree',
                    view_type: 'form',
                    context: context,
                    flags: {
                        action_buttons: true,
                    }
                };
            }
            parent.action_manager.do_action(action);
        },
        show_notify_message: function(message) {
            var sticky = false;
            var parent = this.getParent();
            parent.action_manager.do_notify(_t('Notification'), message, sticky);
        },
        show_warn_message: function(message){
            var sticky = false;
            var parent = this.getParent();
            parent.action_manager.do_warn(_t('Warning'), message, sticky);
        }
    });
    return TimeLog;
});
