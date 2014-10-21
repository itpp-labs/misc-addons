from openerp.osv import osv, fields
import re

def _get_proposal_id(self, cr, uid, ids, name, args, context=None):
    res = {}
    for r in self.browse(cr, uid, ids, context=context):
        proposal_id = self.pool['website_proposal.proposal'].search(cr, uid, [('res_id', '=', r.id), ('res_model', '=', self._name)], context=context)
        res[r.id] = proposal_id and proposal_id[0]
        return res

class crm_lead(osv.Model):
    _inherit = 'crm.lead'

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

class crm_make_sale(osv.osv_memory):
    _inherit = "crm.make.sale"
    def makeOrder(self, cr, uid, ids, context=None):
        res = super(crm_make_sale, self).makeOrder(cr, uid, ids, context)
        res_id = res['res_id']
        if not isinstance(res_id, list):
            res_id = [res_id]
        for order in self.pool['sale.order'].read(cr, uid, res_id, ['id', 'origin'], context=context):
            lead_id = re.search(r'([0-9]+)', order['origin'])
            lead_id = lead_id and lead_id.group(0)
            if not lead_id:
                continue
            lead_id = int (lead_id)
            lead = self.pool['crm.lead'].read(cr, uid, [lead_id], ['proposal_id', 'proposal_template_id'], context=context)
            lead = lead and lead[0]
            if not lead:
                continue
            self.pool['sale.order'].write(cr, uid, [order['id']], {
                'proposal_id': lead.get('proposal_id') and lead.get('proposal_id')[0],
                'proposal_template_id': lead.get('proposal_template_id') and lead.get('proposal_template_id')[0],
            }, context=context)
        return res

class sale_order(osv.Model):
    _inherit = 'sale.order'
    _columns = {
        'proposal_template_id': fields.many2one('website_proposal.template', 'Proposal template'),
        'proposal_id': fields.many2one('website_proposal.proposal', 'Proposal'),
    }
    def create_proposal(self, cr, uid, ids, context=None):
        ctx = (context and context.copy() or {})
        ctx['force_res_model'] = 'sale.order'
        for r in self.read(cr, uid, ids, ['proposal_template_id'], context=context):
            proposal_id = self.pool.get('website_proposal.template').create_proposal(cr, uid, r['proposal_template_id'][0], r['id'], context=ctx)
            self.write(cr, uid, [r['id']], {'proposal_id':proposal_id})
        return True

    def open_proposal(self, cr, uid, ids, context=None):
        r = self.browse(cr, uid, ids[0], context)
        return self.pool['website_proposal.proposal'].open_proposal(cr, uid, [r.proposal_id.id], context=context)
