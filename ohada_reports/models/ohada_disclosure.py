from odoo import models, fields, api, _


# class ResCompanyManager(models.Model):
#     _inherit = "res.company.manager"
#
#     disclosure_contact_person_ids = fields.One2many('ohada.disclosure', 'contact_person_id')
#     disclosure_responsible_employee_ids = fields.One2many('ohada.disclosure', 'responsible_employee_id')


class OhadaDisclosure(models.Model):
    _name = "ohada.disclosure"
    _description = "Process of publishing the Ohada report bundle (pdf)"

    company_id = fields.Many2one('res.company', string='Company')
    fiscalyear_id = fields.Char(string='Fiscal year')
    bundle_report_file_pdf = fields.Binary(string='Bundle report (pdf)', attachment=True)
    bundle_report_file_xlsx = fields.Binary(string='Bundle report (xlsx)', attachment=True)
    number_of_pages = fields.Integer(string='Number of pages')
    number_of_copies = fields.Integer(default=3, string='Number of copies')
    contact_person_id = fields.Many2one('res.company.manager', string='Contact person')
    contact_person_function = fields.Char(related='contact_person_id.function', store=True,
                                          string='Contact person function')
    responsible_employee_id = fields.Many2one('res.company.manager', string='Responsible employee')
    responsible_employee_function = fields.Char(related='responsible_employee_id.function', store=True,
                                                string='Responsible employee function')
    responsible_employee_sign_date = fields.Date(string='Responsible employee sign date')
    chartered_accountant_1 = fields.Many2one('res.partner', string='Chartered accountant 1')
    chartered_accountant_1_sign_date = fields.Date(string='Chartered accountant 1 sign date')
    chartered_accountant_2 = fields.Many2one('res.partner', string='Chartered accountant 2')
    chartered_accountant_2_sign_date = fields.Date(string='Chartered accountant 2 sign date')
    sent2taxoffice_date = fields.Date(string='Sent to tax office date')
    receiving_taxofficer = fields.Char(string='Receiving taxofficer')
    status = fields.Selection(selection=[('draft', 'Draft'), ('report_available', 'Report available'),
                                         ('in_signature', 'In signature'), ('signed', 'Signed'),
                                         ('payment_created', 'Payment created'), ('payment_done', 'Payment done'),
                                         ('sent', 'Sent'), ('archived', 'Archived')],
                              default='draft', string='Status')
    docusign_ids = fields.One2many('docusign.odoo', 'disclosure_id')
    ds_envelope_id = fields.Char(default=False, string='Envelope id', readonly=True)

    @api.multi
    def check_signed_report(self):
        if self.docusign_ids:
            return self.docusign_ids.get_status(self.company_id)
        else:
            self.env['docusign.odoo'].search([]).unlink()
            docusign = self.env['docusign.odoo'].create({'disclosure_id': self.id})
            return docusign.get_status(self.company_id)

    @api.multi
    def send_report_to_signature(self):
        if self.docusign_ids:
            return self.docusign_ids.send_document_for_signing(self.company_id)
            self.env['docusign.odoo'].search([]).unlink()
        else:
            self.env['docusign.odoo'].search([]).unlink()
            docusign = self.env['docusign.odoo'].create({'disclosure_id': self.id})
            return docusign.send_document_for_signing(self.company_id)



class ResPartner(models.Model):
    _inherit = "res.partner"

    chartered_account_type = fields.Selection([('ec', 'Auditor'), ('ca', 'Accountant')], string='Chartered account type')
    chartered_account_id = fields.Char(string='Chartered account id')
