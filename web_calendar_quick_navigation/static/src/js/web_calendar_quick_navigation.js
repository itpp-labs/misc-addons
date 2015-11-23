openerp.web_calendar_quick_navigation = function (session) {

    session.web_calendar.CalendarView.include({
        get_fc_init_options: function() {
            res = this._super();
            res.viewRender = function(view, element) {
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
                } else if (view.name == 'agendaWeek') {
                    $(element).find('th.fc-widget-header').css({'cursor': 'pointer'})
                        .click(function(){
                            var d = new Date();
                            d.setTime(view.start.getTime() + ($(this).prevUntil('tr','th').length-1)*1000*3600*24);
                            view.calendar.changeView('agendaDay');
                            view.calendar.gotoDate(d.getFullYear(), d.getMonth(), d.getDate());
                        });
                }
            };
            res.dayClick = function( date, allDay, jsEvent, view ) {
                if (view.name == 'month' && $(jsEvent.target).hasClass('fc-day-number')) {
                    view.calendar.changeView('agendaDay');
                    view.calendar.gotoDate(date);
                }
            }
            return res;
        }
    });
}