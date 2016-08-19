from openerp import api, models, fields, exceptions

from openerp.osv import fields as old_fields
from openerp.osv import osv
from openerp.tools.translate import _


def _get_active_id(self):
    return self._context.get('active_id')


def _get_active_ids(self):
    return self._context.get('active_ids')


SIGNAL_SELECTION = [
    ('fake_lead_signal', 'lead'),
    ('new', 'new'),
    ('qualified', 'qualified'),
    ('proposal_created', 'proposal_created'),
    ('proposal_sent', 'proposal_sent'),
    ('proposal_confirmed', 'proposal_confirmed'),
]


def fix_sale_case_workflow(sale_case, new_signal):
    print 'fix_sale_case_workflow', sale_case, new_signal
    sale_case.delete_workflow()
    sale_case.create_workflow()
    for signal, label in SIGNAL_SELECTION:
        sale_case.signal_workflow(signal)
        if signal == new_signal:
            break


class create_proposal_lead(models.TransientModel):
    _name = 'sale_mediation_custom.create_proposal_lead'
    sale_case_id = fields.Many2one('crm.lead', default=_get_active_id)
    proposal_template_id = fields.Many2one('website_proposal.template', string='Quotation template')

    @api.multi
    def action_apply(self):
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        #context.pop('default_state', False)
        for r in self:
            assert r.proposal_template_id, 'You have to specify template'
            sale_order = self.sale_case_id.create_sale_order()
            #message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
            # r.sale_case_id.message_post(body=message)

            # CREATE proposal
            proposal_id = self.env['website_proposal.template'].with_context(default_state='draft').create_proposal(r.proposal_template_id.id, r.sale_case_id.id)

            # SAVE new status and sale_order
            r.sale_case_id.signal_workflow('proposal_created')
