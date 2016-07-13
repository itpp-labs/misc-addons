$(document).ready(function() {
    "use strict";
    var TimeLog = openerp.TimeLog = {};
    var storage = localStorage;
    var audio = new Audio();

    TimeLog.Manager = openerp.Widget.extend({
        init: function () {
            this._super();
            var self = this;
            var bus_last = 0;
            Number(storage.getItem("bus_last"))==null ? bus_last=this.bus.last : bus_last=Number(storage.getItem("bus_last"));

            // start the polling
            this.bus = openerp.bus.bus;
            this.bus.last = bus_last;
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
        },
        on_notification: function (notification) {
            var self = this;
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
            var self = this;
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
            /*должны проверить ай ди текущей подзадачи, если они не совпадают то инициализировать заново таймер (новыми данными)
            * после инициализация запускать (таким образом при каждом запуске таймера значения будут обновляться, если сопвпадают ай ди
            * то значит таймер без изминений и он уже инициализирован */
            if (message.status == "play") {
                if (message.active_work_id == new_time_log.work_id) {
                    console.log("play");
                    new_time_log.start_timer();
                } else {
                    new_time_log.load_timer_data(message.active_work_id, message.active_task_id);
                    new_time_log.start_timer();
                }
            } else {
                console.log("stop");
                new_time_log.stop_timer();
            }
            console.log("current work id:", new_time_log.work_id);
            console.log("this work id:", message.active_work_id);
            storage.setItem("bus_last", this.bus.last);
        },
    });

    TimeLog.Conversation = openerp.Widget.extend({
        init: function(){
            this._super();
            var self = this;
            openerp.session = new openerp.Session();
            this.c_manager = new openerp.TimeLog.Manager();

            this.stopline = '';
            this.work_id = '';
            this.task_id = '';
            this.status = 'stopped';
            this.times = [0,0,0,0];
			this.initial_planed_hours = 0;

            this.before_timer0 = 10;
			this.timer0 = 15;

			this.planed_timer2 = 5*60*60;
			this.big_planed_timer2 = 0;

			this.planed_timer3 = 30*60*60;
			this.big_planed_timer3 = 0;

            this.audio_format = '';

            console.log("Initial timer");
            this.start();
        },
        start: function() {
            var self = this;
            openerp.session.rpc("/timelog/init", {}).then(function(resultat){
                self.stopline = resultat.stopline;
                self.task_id = resultat.task_id;
                self.work_id = resultat.work_id;
                self.initial_planed_hours = resultat.planned_hours;
                self.times = [
                    resultat.init_first_timer,
                    resultat.init_second_timer,
                    resultat.init_third_timer,
                    resultat.init_fourth_timer,
                    resultat.name_first_timer
                ];
                console.log(self.times[0]);
                console.log(self.times[1]);
                self.add_title(resultat.name_first_timer, resultat.description_second_timer);
                self.check_audio();
            });
        },

        //loading data for timer
        load_timer_data: function(work_id, task_id){
            var self = this;
          console.log("load new timer");
            openerp.session.rpc("/timelog/get_timer", {"work_id": work_id, "task_id": task_id}).then(function(resultat){
                console.log(resultat);
                self.times[0] = resultat.init_first_timer;
                if (resultat.init_second_timer) {
                    self.times[1] = resultat.init_second_timer;
                    self.task_id = task_id;
                }
                self.add_title(resultat.name_first_timer, resultat.description_second_timer);
                self.updateView();
                self.work_id = work_id;
            });
        },

        check_audio: function() {
            if (typeof(Audio) === "undefined") {
                return;
            }
            this.audio_format= audio.canPlayType("audio/ogg; codecs=vorbis") ? ".ogg" : ".mp3";
            this.updateView();
		},

        updateView : function() {
            var element = document.getElementById("timelog_timer");
            if(!element) {
                console.log("not element");
                return false;
            }

			for (var i = 0; i < 4; i++) {
			  this.updateClock(i, this.times[i]);
			}
		},

        updateClock : function(id, time) {
			var element = document.getElementById("clock"+id);
            if(!element) {
                return false;
            }

			var formattedTime = this.formatTime(id, time);
			element.innerHTML = formattedTime;
			var self = this;
            /*когда условие выполнилось нужно остановить таймер и отправить запрос на сервер с сохранением даты остановки таймер или там при достижении
            * 2 часов остановить таймер */

			switch(id) {
                case 0: {
                    if ( this.times[0] == this.before_timer0) {
                        $('#clock0').css('color','orange');
                        self.playAudio(0);
                    }
                    if ( this.times[0] > this.before_timer0) {
                        $('#clock0').css('color','orange');
                    }
                    if ( this.times[0] == this.timer0) {
                        $('#clock0').css('color','red');
                        this.addClass(0, "expired");
                        var element = document.getElementById("clock0");
                        this.startAnim(element, 500, 10*500);
                        this.stop_timer();
                    }
                } break;

                case 1:  {
                    if (this.times[1] >= this.initial_planed_hours) {
                        $('#clock1').css('color','orange');
                    }
                    if (this.times[1] >= 2*this.initial_planed_hours) {
                        $('#clock0').css('color','red');
                        this.addClass(1, "expired");
                    }
                } break;

                case 2: {
                    if (this.times[2] >= this.planed_timer2){
                        $('#clock2').css('color','yellow');
                    }
                    if (this.times[2] >= this.big_planed_timer2) {
                        $('#clock2').css('color','#00f900');
                    }
                } break;

                case 3: {
                    if (this.times[3] == this.planed_timer3){
                        $('#clock3').css('color','#00f900');
                        self.playAudio(2);
                    }
                    if (this.times[3] > this.planed_timer3){
                        $('#clock3').css('color','#00f900');
                    }
                    if (this.times[3] == this.big_planed_timer3) {
                        $('#clock3').css('color','rgb(0, 144, 249)');
                        self.playAudio(3);
                    }
                    if (this.times[3] >= this.big_planed_timer3) {
                        $('#clock3').css('color','rgb(0, 144, 249)');
                    }
                } break;

                default:
                    console.log("NONE");
				break;
            }
        },

        addClass : function(id, className) {
			var element = document.getElementById("clock"+id);
			element.className += " " + className;
		},

		removeClass : function(id, className) {
			var element = document.getElementById("clock"+id);
			var exp = new RegExp(className);
			element.className = element.className.replace( exp , '' );
		},

        formatTime : function(id, time) {
            var minutes = Math.floor(time / 60);
            var seconds = Math.floor(time % 60);
            var hours = Math.floor(minutes / 60);
            minutes = Math.floor(minutes % 60);

            var result = "";
            if (hours < 10) result +="0";
            result += hours + ":";
            if (minutes < 10) result += "0";

            if (id == 0) {
                result += minutes + ":";
                if (seconds < 10) result += "0"; result += seconds;
            }
            else result += minutes;


            if (id == 0) console.log(result);

            return result;
		},

        setIntervalTimer: function() {
			this.timer = window.setInterval(this.countDownTimer, 1000);
		},

        countDownTimer: function() {
			for (var i = 0; i < 4; i++) {
			  new_time_log.times[i]++;
			  new_time_log.updateClock(i, new_time_log.times[i]);
			}
		},

        start_timer: function(){
			if (this.status == 'running'){
				return false;
			}
			var self = this;
			this.status = 'running';
			this.setIntervalTimer();
			for (var i = 0; i < 4; i++) {
			  this.addClass(i, "running");
			}
		},

		stop_timer: function(){
			if (this.status == 'stopped'){
				return false;
			}
			var self = this;
			this.status = 'stopped';
			for (var i = 0; i < 4; i++) {
			  this.removeClass(i, "running");
			}
			clearTimeout(this.timer);
            console.log(self.times[0]);
            console.log(self.times[1]);
		},

        startAnim: function (element, interval, time) {
			var self = this;
			element.animTimer = setInterval(function () {
			if (element.style.display == "none")  {
				element.style.display = "";
				self.playAudio(1);
			}
			else
				element.style.display = "none";
			}, interval);
			setTimeout(function(){
				self.stopAnim(element);
			}, time);
		},

		stopAnim: function(element){
			clearInterval(element.animTimer);
			element.style.display = "";
		},

		playAudio: function(id) {
			var audio_name = id + '.' + this.audio_format;
            audio.src = openerp.session.url("/project_timelog/static/src/audio/"+id+ this.audio_format);
			audio.play();
		},

        add_title: function(first_timer_name, description_second_timer) {
            $('#clock0').attr("title", first_timer_name);
            $('#clock1').attr("title", description_second_timer);
        }
    });

    var new_time_log = new TimeLog.Conversation(this);

	$( "#clock0" ).click(function() {
		console.log("click!");
	});

    console.log(openerp.session);
    console.log("session");

});