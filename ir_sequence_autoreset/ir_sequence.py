# -*- coding: utf-8 -*-
#
#
#    Auto reset sequence by year,month,day
#    Copyright 2013 wangbuke <wangbuke@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import osv, fields
from openerp.tools.translate import _


class IrSequence(osv.osv):
    _inherit = 'ir.sequence'

    _columns = {
        'auto_reset': fields.boolean('Auto Reset'),
        'reset_period': fields.selection(
            [('year', 'Every Year'), ('month', 'Every Month'), ('woy', 'Every Week'), ('day', 'Every Day'), ('h24', 'Every Hour'), ('min', 'Every Minute'), ('sec', 'Every Second')],
            'Reset Period', required=True),
        'reset_time': fields.char('Name', size=64, help=""),
        'reset_init_number': fields.integer('Reset Number', required=True, help="Reset number of this sequence"),
    }

    _defaults = {
        'auto_reset': False,
        'reset_period': 'month',
        'reset_init_number': 1,
    }

    def _next(self, cr, uid, seq_ids, context=None):
        if not seq_ids:
            return False
        if context is None:
            context = {}
        force_company = context.get('force_company')
        if not force_company:
            force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        sequences = self.read(cr, uid, seq_ids, ['name', 'company_id', 'implementation', 'number_next', 'prefix', 'suffix', 'padding', 'number_increment', 'auto_reset', 'reset_period', 'reset_time', 'reset_init_number'])
        preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company]
        seq = preferred_sequences[0] if preferred_sequences else sequences[0]
        if seq['implementation'] == 'standard':
            current_time = ':'.join([seq['reset_period'], self._interpolation_dict().get(seq['reset_period'])])
            if seq['auto_reset'] and current_time != seq['reset_time']:
                cr.execute("UPDATE ir_sequence SET reset_time=%s WHERE id=%s ", (current_time, seq['id']))
                self._alter_sequence(cr, seq['id'], seq['number_increment'], seq['reset_init_number'])
                cr.commit()

            cr.execute("SELECT nextval('ir_sequence_%03d')" % seq['id'])
            seq['number_next'] = cr.fetchone()
        else:
            cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (seq['id'],))
            cr.execute("UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s ", (seq['id'],))
        d = self._interpolation_dict()
        try:
            interpolated_prefix = self._interpolate(seq['prefix'], d)
            interpolated_suffix = self._interpolate(seq['suffix'], d)
        except ValueError:
            raise osv.except_osv(_('Warning'), _('Invalid prefix or suffix for sequence \'%s\'') % (seq.get('name')))
        return interpolated_prefix + '%%0%sd' % seq['padding'] % seq['number_next'] + interpolated_suffix


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
