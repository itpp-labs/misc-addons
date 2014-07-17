# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class mail_thread(osv.Model):
    _inherit = "mail.thread"

    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context={}):

        def convert_for_display(value, col_info):
            if not value and col_info['type'] == 'boolean':
                return 'False'
            if not value:
                return ''
            if col_info['type'] == 'many2one':
                return value.name_get()[0][1]
            if col_info['type'] == 'selection':
                return dict(col_info['selection'])[value]
            return value

        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message

        if not tracked_fields:
            return True

        update_fields = [f for f in tracked_fields]

        for browse_record in self.browse(cr, uid, ids, context=context):
            p = getattr(browse_record, 'partner_id', None)
            if p:
                browse_record._context.update({'lang':p.lang})

            initial = initial_values[browse_record.id]
            changes = set()
            tracked_values = {}

            # update translation
            tracked_fields = self._get_tracked_fields(cr, uid, update_fields, browse_record._context)

            # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
            for col_name, col_info in tracked_fields.items():
                initial_value = initial[col_name]
                record_value = getattr(browse_record, col_name)

                if record_value == initial_value and getattr(self._all_columns[col_name].column, 'track_visibility', None) == 'always':
                    tracked_values[col_name] = dict(col_info=col_info['string'],
                                                        new_value=convert_for_display(record_value, col_info))
                elif record_value != initial_value and (record_value or initial_value):  # because browse null != False
                    if getattr(self._all_columns[col_name].column, 'track_visibility', None) in ['always', 'onchange']:
                        tracked_values[col_name] = dict(col_info=col_info['string'],
                                                            old_value=convert_for_display(initial_value, col_info),
                                                            new_value=convert_for_display(record_value, col_info))
                    if col_name in tracked_fields:
                        changes.add(col_name)
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtypes = []
            for field, track_info in self._track.items():
                if field not in changes:
                    continue
                for subtype, method in track_info.items():
                    if method(self, cr, uid, browse_record, context):
                        subtypes.append(subtype)

            posted = False
            for subtype in subtypes:
                subtype_rec = self.pool.get('ir.model.data').xmlid_to_object(cr, uid, subtype, context=context)
                if not (subtype_rec and subtype_rec.exists()):
                    _logger.debug('subtype %s not found' % subtype)
                    continue
                message = format_message(subtype_rec.description if subtype_rec.description else subtype_rec.name, tracked_values)
                self.message_post(cr, uid, browse_record.id, body=message, subtype=subtype, context=context)
                posted = True
            if not posted:
                message = format_message('', tracked_values)
                self.message_post(cr, uid, browse_record.id, body=message, context=context)
        return True
