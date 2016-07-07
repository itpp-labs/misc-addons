$( document ).ready(function() {
	"use strict";
	var audio = new Audio();
	var Common = {
		initial_timer: function(){
            var self = this;
			this.status = 'stop';
			this.initialTimes = [2*60*61,10*601,5*60*60,50*60*60];
			this.times = [2*60*61,10*601,5*60*60,50*60*60];
			this.initial_planed_hours = 3000;
			
			this.before_timer0 = 2*60*60-20*60;
			this.timer0 = 2*60*60;
			
			this.planed_timer2 = 5*60*60;
			this.big_planed_timer2 = 6*60*60;
			
			this.planed_timer3 = 30*60*60;
			this.big_planed_timer3 = 40*60*60;
			
			this.audio_format = '';

			this.check_audio();
		},
		
		check_audio: function() {
			var self = this;
			
			var canPlayMP3 = !!audio.canPlayType && audio.canPlayType('audio/mp3') != "";
			var canPlayWAV = !!audio.canPlayType && audio.canPlayType('audio/wav') != "";
			var canPlayOGG = !!audio.canPlayType && audio.canPlayType('audio/ogg') != "";
			var canPlayMP4 = !!audio.canPlayType && audio.canPlayType('audio/mp4') != "";
			
			if(canPlayMP3) {
			 self.audio_format = 'mp3';
			 this.updateView();
			 return false;
			}
			
			if(canPlayOGG) {
			 self.audio_format = 'ogg';
			 this.updateView();
			 return false;
			}
			
			if(canPlayWAV) {
			 self.audio_format = 'wav';
			 this.updateView();
			 return false;
			}

			if(canPlayMP4) {
			 self.audio_format = 'mp4';
			 this.updateView();
			 return false;
			} else {
				console.log('Browser does not support music format');
			}
		},
		
		start_timer: function(){
			var self = this;
			console.log("start timer");
			this.status = 'start';
		},
		
		stop_timer: function(){
			var self = this;
			this.status = 'stop';
			console.log("stop timer");
		},
		
		updateView : function() {
			for (var i = 0; i < 4; i++) {
			  this.updateClock(i, this.times[i]);
			}
		},
			
		updateClock : function(id, time) {
			var element = document.getElementById("clock"+id);
			var formattedTime = this.formatTime(time);
			element.innerHTML = formattedTime;
			var self = this;
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
					var element = document.getElementById("clock0")
					this.startAnim(element, 500, 10*500);
				}
			  }
				break;

			  case 1:  {
				if (this.times[1] >= this.initial_planed_hours) {
					$('#clock1').css('color','orange');
				}
				if (this.times[1] >= 2*this.initial_planed_hours) {
					$('#clock0').css('color','red');
					this.addClass(1, "expired");
				}
			  }
				break;
				
			  case 2: {
				if (this.times[2] >= this.planed_timer2){
					$('#clock2').css('color','yellow');
				}
				if (this.times[2] >= this.big_planed_timer2) {
					$('#clock2').css('color','#00f900');
				}
			  }
				break;
				
			  case 3: 
			  	if (this.times[3] == this.planed_timer2){
					$('#clock3').css('color','#00f900');
					self.playAudio(2);
				}
				if (this.times[3] > this.planed_timer2){
					$('#clock3').css('color','#00f900');
				}
				
				if (this.times[3] == this.big_planed_timer2) {
					$('#clock3').css('color','rgb(0, 144, 249)');
					self.playAudio(3);
				}
				if (this.times[3] >= this.big_planed_timer2) {
					$('#clock3').css('color','rgb(0, 144, 249)');
				}
				break;

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
		
		formatTime : function(time) {
            var minutes = Math.floor(time / 60);
            var seconds = Math.floor(time % 60);
            var hours = Math.floor(minutes / 60);
            minutes = Math.floor(minutes % 60);

            var result = "";
            if (hours < 10) result +="0";
            result += hours + ":";
            if (minutes < 10) result += "0";
            result += minutes + ":";
            if (seconds < 10) result += "0";
            result += seconds;

            return result;
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
			audio.src = id + '.' + this.audio_format;
			audio.play();
		},
	}
	
	Common.initial_timer();
	
	$( "#start" ).click(function() {
		Common.start_timer();
	});
	$( "#stop" ).click(function() {
		Common.stop_timer();
	});
	$( "#clock0" ).click(function() {
		Common.stop_timer();
	});
	
	$('[data-tooltip]').addClass('tooltip');
	$('.tooltip').each(function() {  
		$(this).append('<span class="tooltip-content">' + $(this).attr('data-tooltip') + '</span>');  
	});	
	$('.tooltip').mouseover(function(){
		$(this).children('.tooltip-content').css('visibility','visible');
	}).mouseout(function(){
		$(this).children('.tooltip-content').css('visibility','hidden');
	})	
	
});
