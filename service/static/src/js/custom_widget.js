odoo.define('service.custom_widget', function(require) {

var core = require('web.core');
var data = require('web.data');
var formats = require('web.field_utils');
var rpc = require('web.rpc');
var time = require('web.time');
var utils = require('web.utils');
var widgets = require('web.Widget');
var local_storage = require('web.local_storage');
var CalendarView = require('web.CalendarView');
var CalendarRenderer = require('web.CalendarRenderer');
var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

CalendarRenderer.include({
    init: function () {
        this._super.apply(this, arguments);
        // var attrs = this.fields_view.arch.attrs;
		// this.state_data = attrs.state_data;
	},


   	event_data_transform: function(evt) {
        this._super.apply(this, arguments);
        var self = this;
        var date_start;
        var date_stop;
        var date_delay = evt[this.date_delay] || 1.0,
            all_day = this.all_day ? evt[this.all_day] : false,
            res_computed_text = '',
            the_title = '',
            attendees = [];

        if (!this.all_day) {
            date_start = time.auto_str_to_date(evt[this.date_start]);
            date_stop = this.date_stop ? time.auto_str_to_date(evt[this.date_stop]) : null;
        } else {
            date_start = time.auto_str_to_date(evt[this.date_start].split(' ')[0],'start');
            date_stop = this.date_stop ? time.auto_str_to_date(evt[this.date_stop].split(' ')[0],'start') : null;
        }
        if (this.info_fields) {
            var temp_ret = {};
            res_computed_text = this.how_display_event;

            _.each(this.info_fields, function (fieldname) {
                var value = evt[fieldname];
                if (_.contains(["many2one"], self.fields[fieldname].type)) {
                    if (value === false) {
                        temp_ret[fieldname] = null;
                    }
                    else if (value instanceof Array) {
                        temp_ret[fieldname] = value[1]; // no name_get to make
                    }
                    else if (_.contains(["date", "datetime"], self.fields[fieldname].type)) {
                        temp_ret[fieldname] = formats.formatFloatTime(value, self.fields[fieldname]);
                    }
                    else {
                        throw new Error("Incomplete data received from dataset for record " + evt.id);
                    }
                }
                else if (_.contains(["one2many","many2many"], self.fields[fieldname].type)) {
                    if (value === false) {
                        temp_ret[fieldname] = null;
                    }
                    else if (value instanceof Array)  {
                        temp_ret[fieldname] = value; // if x2many, keep all id !
                    }
                    else {
                        throw new Error("Incomplete data received from dataset for record " + evt.id);
                    }
                }
                else {
                    temp_ret[fieldname] = value;
                }
                res_computed_text = res_computed_text.replace("["+fieldname+"]",temp_ret[fieldname]);
            });


            if (res_computed_text.length) {
                the_title = res_computed_text;
            }
            else {
                var res_text= [];
                _.each(temp_ret, function(val,key) {
                    if( typeof(val) === 'boolean' && val === false ) { }
                    else { res_text.push(val); }
                });
                the_title = res_text.join(', ');
            }
            the_title = _.escape(the_title);


            var the_title_avatar = '';

            if (! _.isUndefined(this.attendee_people)) {
                var MAX_ATTENDEES = 3;
                var attendee_showed = 0;
                var attendee_other = '';

                _.each(temp_ret[this.attendee_people],
                    function (the_attendee_people) {
                        attendees.push(the_attendee_people);
                        attendee_showed += 1;
                        if (attendee_showed<= MAX_ATTENDEES) {
                            if (self.avatar_model !== null) {
                                       the_title_avatar += '<img title="' + _.escape(self.all_attendees[the_attendee_people]) + '" class="o_attendee_head"  \
                                                        src="/web/image/' + self.avatar_model + '/' + the_attendee_people + '/image_small"></img>';
                            }
                            else {
                                if (!self.colorIsAttendee || the_attendee_people != temp_ret[self.color_field]) {
                                        var tempColor = (self.all_filters[the_attendee_people] !== undefined)
                                                    ? self.all_filters[the_attendee_people].color
                                                    : (self.all_filters[-1] ? self.all_filters[-1].color : 1);
                                        the_title_avatar += '<i class="fa fa-user o_attendee_head o_underline_color_'+tempColor+'" title="' + _.escape(self.all_attendees[the_attendee_people]) + '" ></i>';
                                }//else don't add myself
                            }
                        }
                        else {
                                attendee_other += _.escape(self.all_attendees[the_attendee_people]) +", ";
                        }
                    }
                );
                if (attendee_other.length>2) {
                    the_title_avatar += '<span class="o_attendee_head" title="' + attendee_other.slice(0, -2) + '">+</span>';
                }
            }
        }

        if (!date_stop && date_delay) {
            var m_start = moment(date_start).add(date_delay,'hours');
            date_stop = m_start.toDate();
        }

        var r = {
            'start': moment(date_start).toString(),
            'end': moment(date_stop).toString(),
            'title': the_title,
            'attendee_avatars': the_title_avatar,
            'allDay': (this.fields[this.date_start].type == 'date' || (this.all_day && evt[this.all_day]) || false),
            'id': evt.id,
            'attendees':attendees
        };
        var color_key = evt[this.state_data];

        if (!self.useContacts || self.all_filters[color_key] !== undefined) {
            if (color_key) {
                // if (typeof color_key === "object") {
                //     color_key = color_key[0];
                // }
                var colr = 0;
                if (color_key === "QUOTE"){
                    colr = 4;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'APPROVE'){
                    colr = 8;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'PARTS'){
                    colr = 13;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'PICKUP'){
                    colr = 18;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'INSPECT'){
                    colr= 3;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'LIFT'){
                    colr = 24;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'TEST'){
                    colr= 24;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'COMPLETE'){
                    colr= 1;
                    r.className = 'o_calendar_color_'+ colr;
                }
                else if (color_key === 'DELEVER'){
                    colr = 15;
                    r.className = 'o_calendar_color_'+ colr;
                }
                // r.className = 'o_calendar_color_'+ this.get_color(color_key);
            }
        } else { // if form all, get color -1
            r.className = 'o_calendar_color_'+ (self.all_filters[-1] ? self.all_filters[-1].color : 1);

        }
        return r;
   	},

	fetch_data: function() {
        	return $.when(this._rpc({
                    	model: 'service_drm.dashboard',
                    	method: 'compute_count_all',
                    	args: [],
                	}));
    },

    _render: function() {
        this._super();
        var self = this;
        var data = {};

        return this.fetch_data().then(function(result){
            var approve=result['count_approve'];
            console.log(result);
            data = {
                'approve': result['count_approve'],
                'quote': result['count_quote'],
                'parts': result['count_parts'],
                'pickup': result['count_pickups'],
                'inspect': result['count_inspect'],
                'lift': result['count_lift'],
                'test': result['count_test'],
                'complete': result['count_complete'],
                'deliver': result['count_deliver'],

                'repair_done': result['count_repair_done'],
                'repair_pending': result['orders_repair_pending'],
            };
            $('.o_calendar_contacts2').html(QWeb.render('CalendarView.sidebar.service_cal', {filters: data}));
            
        });
    },
});
});
