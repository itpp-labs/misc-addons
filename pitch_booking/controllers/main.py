# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.http import request

try:
    from openerp.addons.website_booking_calendar.controllers.main import WebsiteBookingCalendar as Controller
except ImportError:
    class Controller(object):
        pass


class WebsiteBookingCalendar(Controller):

    def _get_resources(self, params):
        venue_id, pitch_id = params.get('venue'), params.get('pitch')
        cr, uid, context = request.cr, request.uid, request.context
        pitch_obj = request.registry['pitch_booking.pitch']
        venue_obj = request.registry['pitch_booking.venue']
        if not venue_id:
            venues = venue_obj.search(cr, uid, [], context=context)
            venue_id = venues[0] if venues else None
        if pitch_id:
            return pitch_obj.browse(cr, uid, int(pitch_id), context=context).resource_id
        elif venue_id:
            pitch_ids = pitch_obj.search(cr, uid, [('venue_id', '=', int(venue_id))], context=context)
            return [p.resource_id for p in pitch_obj.browse(cr, SUPERUSER_ID, pitch_ids, context=context)]
        return super(WebsiteBookingCalendar, self)._get_resources(params)

    def _get_values(self, params):
        values = super(WebsiteBookingCalendar, self)._get_values(params)
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        venue_obj = request.registry['pitch_booking.venue']
        venues = venue_obj.browse(cr, uid, venue_obj.search(cr, uid, [], context=context), context=context)
        values.update({
            'venues': venues,
            'active_venue': int(params.get('venue')) if params.get('venue') else (venues[0].id if venues else None)
        })
        return values
