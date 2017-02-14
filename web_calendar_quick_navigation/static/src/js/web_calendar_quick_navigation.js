openerp.web_calendar_quick_navigation = function (session) {
    var QWeb = session.web.qweb;

    session.web_calendar.CalendarView.include({
        build_quick_panel_monthes(view, element) {
            var monthes = view.calendar.option('monthNamesShort');
            var currentM = view.start.getMonth();
            var len = monthes.length;
            var monthPeriod = [];
            for (var i=currentM-6-6; i<=currentM+5+6; i++) {
                var item = {
                    current: i == currentM,
                    month: i,
                    name: monthes[i],
                    year: view.start.getFullYear(),
                };
                if (i < 0) {
                    item.month = len + i;
                    item.name = monthes[len + i];
                    item.year -= 1;
                } else if (i >= len) {
                    item.month = i - len;
                    item.name = monthes[i - len];
                    item.year += 1;
                }
                monthPeriod.push(item);
            }
            if ($(element).find('div.quick_monthes').length) {
                $(element).find('div.quick_monthes').replaceWith($(QWeb.render("CalendarView.quick_navigation.panel.monthes", {
                    'monthes': monthPeriod
                })));
            } else {
                $(element).prepend($(QWeb.render("CalendarView.quick_navigation.panel.monthes", {
                    'monthes': monthPeriod
                })));
            }
            $(element).on ('click', 'div.quick_monthes a', function() {
                view.calendar.gotoDate($(this).data('year'), $(this).data('month'), 1);
            });
        },
        build_quick_panel_weeks(view, element) {
            var weekPeriod = [];
            var ts = view.start.getTime();
            for (var i=ts-4*86400000*7; i<=ts+3*86400000*7; i+=86400000*7) {
                var d = new Date();
                d.setTime(i);
                dE = new Date();
                dE.setTime(i+86400000*7);
                weekPeriod.push({
                    current: i == ts,
                    date: i,
                    name: view.calendar.formatDate(d, 'ddMMM') + '-'
                        + view.calendar.formatDate(dE, 'ddMMM')
                });
            }
            if ($(element).find('div.quick_weeks').length) {
                $(element).find('div.quick_weeks').replaceWith($(QWeb.render("CalendarView.quick_navigation.panel.weeks", {
                    'weeks': weekPeriod
                })));
            } else {
                $(element).prepend($(QWeb.render("CalendarView.quick_navigation.panel.weeks", {
                    'weeks': weekPeriod
                })));
            }
            $(element).on ('click', 'div.quick_weeks a', function() {
                d = new Date();
                d.setTime(parseInt($(this).data('date')));
                view.calendar.gotoDate(d.getFullYear(), d.getMonth(), d.getDate());
            });
        },
        view_render: function(self, view, element) {
            // make week names clickable for quick navigation
            if (view.name == 'month') {
                var $td = $(element).find('td.fc-week-number');
                $td.css({'cursor': 'pointer'}).find('div').html('&rarr;');
                $td.click(function(){
                    var day = $(this).next().data('date');
                    view.calendar.changeView('agendaWeek');
                    view.calendar.gotoDate(parseInt(day.substring(0,4)), 
                        parseInt(day.substring(5,7))-1, parseInt(day.substring(8,10)));
                });
                self.build_quick_panel_monthes(view, element);
            } else if (view.name == 'agendaWeek') {
                $(element).find('th.fc-widget-header').css({'cursor': 'pointer'})
                    .click(function(){
                        var d = new Date();
                        d.setTime(view.start.getTime() + ($(this).prevUntil('tr','th').length-1)*1000*3600*24);
                        view.calendar.changeView('agendaDay');
                        view.calendar.gotoDate(d.getFullYear(), d.getMonth(), d.getDate());
                    });
                self.build_quick_panel_weeks(view, element);
            }
        },
        select: function (self, start_date, end_date, all_day, _js_event, _view) {
            var is_day = false;
            if (_view.name == 'month') {
                $(document.elementsFromPoint(_js_event.originalEvent.x, _js_event.originalEvent.y)).each(function(){
                    if ($(this).hasClass('fc-day-number')) {
                        _view.calendar.changeView('agendaDay');
                        _view.calendar.gotoDate(start_date);
                        is_day = true;
                        return;
                    }
                });
            }
            if (is_day) {
                return;
            }
            var data_template = self.get_event_data({
                start: start_date,
                end: end_date,
                allDay: all_day,
            });
            self.open_quick_create(data_template);

        },
        get_fc_init_options: function() {
            var res = this._super();
            var self = this;
            res.viewRender = function(view, element) {
                self.view_render(self, view, element);
            };
            res.select = function (start_date, end_date, all_day, _js_event, _view) {
                self.select(self, start_date, end_date, all_day, _js_event, _view);
            };
            return res;
        }
    });
};
