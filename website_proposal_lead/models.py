from openerp.osv import osv, fields

class crm_lead(osv.Model):
    _inherit = 'crm.lead'
    def _get_proposal_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for r in self.browse(cr, uid, ids, context=context):
            proposal_id = self.pool['website_proposal.proposal'].search(cr, uid, [('res_id', '=', r.id), ('res_model', '=', self._name)], context=context)
            res[r.id] = proposal_id and proposal_id[0]
        return res

    _columns = {
        'proposal_template_id': fields.many2one('website_proposal.template', 'Proposal template'),
        'proposal_id': fields.function(_get_proposal_id, type='many2one', obj='website_proposal.proposal', string='Proposal'),
    }

    def create_proposal(self, cr, uid, ids, context=None):
        for r in self.read(cr, uid, ids, ['proposal_template_id'], context=context):
            proposal_id = self.pool.get('website_proposal.template').create_proposal(cr, uid, r['proposal_template_id'][0], r['id'], context=context)
        return True

    def open_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].open_proposal(cr, uid, [r.proposal_id.id], context=context)
