# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import uuid
import time
import datetime
from openerp import tools

import openerp.addons.decimal_precision as dp

from openerp.addons.email_template.email_template import mako_template_env

class website_proposal_template(osv.osv):
    _name = "website_proposal.template"
    _description = "Proposal Template"
    _columns = {
        'name': fields.char('Proposal Template', required=True),

        'head': fields.text('Html head'),
        'page_header': fields.text('Page header'),
        'website_description': fields.html('Description'),
        'page_footer': fields.text('Page footer'),

        'res_model': fields.char('Model', help="The database object this template will be applied to"),
    }
    def open_template(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/website_proposal/template/%d' % ids[0]
        }


    def create_proposal(self, cr, uid, template_id, res_id, context=None):
        if not template_id:
            return False
        if isinstance(template_id, list):
            template_id = template_id[0]

        template = self.pool.get('website_proposal.template').browse(cr, uid, template_id, context=context)

        vals = {'template_id': template_id,
                'head': template.head,
                'page_header': template.page_header,
                'website_description': template.website_description,
                'page_footer': template.page_footer,
                'res_id': res_id,
                'res_model': context.get('force_res_model') or template.res_model,
                }

        proposal_id = self.pool.get('website_proposal.proposal').create(cr, uid, vals, context)
        return proposal_id


class website_proposal(osv.osv):
    _name = 'website_proposal.proposal'
    _rec_name = 'id'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'access_token': fields.char('Security Token', required=True, copy=False),
        'template_id': fields.many2one('website_proposal.template', 'Quote Template', readonly=True),
        'head': fields.text('Html head'),
        'page_header': fields.text('Page header'),
        'website_description': fields.html('Description'),
        'page_footer': fields.text('Page footer'),

        'res_model': fields.char('Model', readonly=True, help="The database object this is attached to"),
        'res_id': fields.integer('Resource ID', readonly=True, help="The record id this is attached to", select=True),
        'sign': fields.binary('Singature'),
        'signer': fields.binary('Signer'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Signed'),
        ]),
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'access_token': lambda self, cr, uid, ctx={}: str(uuid.uuid4()),
        'company_id': _get_default_company,
        'state': 'draft',
    }

    def open_proposal(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/website_proposal/%s' % (ids[0])
        }
    def create(self, cr, uid, vals, context=None):
        record = self.pool.get(vals.get('res_model')).browse(cr, uid, vals.get('res_id'))

        mako = mako_template_env.from_string(tools.ustr(vals.get('website_description')))
        website_description = mako.render({'record':record})

        vals['website_description'] = website_description
        new_id = super(website_proposal, self).create(cr, uid, vals, context=context)
        return new_id
