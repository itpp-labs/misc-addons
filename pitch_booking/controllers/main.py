from openerp import http
from openerp.http import request

try:
    from openerp.addons.website_booking_calendar.controllers.main import website_booking_calendar as controller
except ImportError:
    class controller(object):
        pass


class website_booking_calendar(controller):

    def _get_resources(self, params):
        venue_id, pitch_id = params.get('venue'), params.get('pitch')
        cr, uid, context = request.cr, request.uid, request.context
        resource_obj = request.registry['resource.resource']
        pitch_obj = request.registry['pitch_booking.pitch']
        if pitch_id:
            return pitch_obj.browse(cr, uid, int(pitch_id), context=context).resource_id
        elif venue_id:
            pitch_ids = pitch_obj.search(cr, uid, [('venue_id','=',int(venue_id))], context=context)
            return [p.resource_id for p in pitch_obj.browse(cr, uid, pitch_ids, context=context)]
        return super(website_booking_calendar, self)._get_resources(params)

    def _get_values(self, params):
        values = super(website_booking_calendar, self)._get_values(params)
        cr, uid, context = request.cr, request.uid, request.context
        venue_obj = request.registry['pitch_booking.venue']
        values.update({
            'venues': venue_obj.browse(cr, uid, venue_obj.search(cr, uid, [], context=context), context=context),
            'active_venue': int(params.get('venue')) if params.get('venue') else None
        })
        return values
