from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import UserError
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, Document


class DocuSignOdoo(models.Model):
    _name = "docusign.odoo"

    access_token = fields.Char(default='')
    disclosure_id = fields.Many2one('ohada.disclosure')


    def authorization(self, company):
        response_type = 'code'
        scope = 'signature'
        client_id = company.ds_integration_key
        redirect_uri = self.env['ir.config_parameter'].sudo().get_param('report.url') or \
                       self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirect_uri += '/docusign'

        client_action = {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://account-d.docusign.com/oauth/auth' + '?response_type=' + response_type + '&scope=' + scope + '&client_id=' + client_id + '&redirect_uri=' + redirect_uri,
        }

        return client_action

    def send_document_for_signing(self, company):
        token = self.env['docusign.odoo.token'].search([])
        if token:
            self.write({'access_token': token[-1].code})
        info = self.get_info()
        if info.get('error'):
            return self.authorization(company)
        account_id = info['accounts'][0].get('account_id')
        account_name = info['accounts'][0].get('account_name')

        signer_email = company.ds_email
        base_path = company.ds_base_uri + '/restapi'

        base64_file_content = self.disclosure_id.bundle_report_file_pdf.decode("utf-8")
        document_name = 'Bundle report ' + self.disclosure_id.fiscalyear_id

        document = Document(  # create the DocuSign document object
            document_base64=base64_file_content,
            name=document_name,  # can be different from actual file name
            file_extension='pdf',  # many different document types are accepted
            document_id=1  # a label used to reference the doc
        )

        # Create the signer recipient model
        signer = Signer(  # The signer
            email=signer_email, name=account_name, recipient_id="1", routing_order="1")

        # Create a sign_here tab (field on the document)
        sign_here = SignHere(  # DocuSign SignHere field/tab
            document_id='1', page_number='1', recipient_id='1', tab_label='SignHereTab',
            x_position='480', y_position='750')

        # Add the tabs model (including the sign_here tab) to the signer
        signer.tabs = Tabs(sign_here_tabs=[sign_here])  # The Tabs object wants arrays of the different field/tab types

        # Next, create the top level envelope definition and populate it.
        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign this document " + document_name,
            documents=[document],  # The order in the docs array determines the order in the envelope
            recipients=Recipients(signers=[signer]),  # The Recipients object wants arrays for each recipient type
            status="sent"  # requests that the envelope be created and sent.
        )

        # Ready to go: send the envelope request
        api_client = ApiClient()
        api_client.host = base_path
        api_client.set_default_header("Authorization", "Bearer " + self.access_token)

        envelope_api = EnvelopesApi(api_client)
        try:
            results = envelope_api.create_envelope(account_id, envelope_definition=envelope_definition)
            self.disclosure_id.write({'ds_envelope_id': results.envelope_id, 'status': 'in_signature'})
            self.disclosure_id = False
        except Exception as e:
            raise UserError(
                _("Method doesn't work. Wrong credentials?\n%s" % (e))
            )

    def get_status(self, company):
        token = self.env['docusign.odoo.token'].search([])
        if token:
            self.write({'access_token': token[-1].code})
        info = self.get_info()
        if info.get('error'):
            return self.authorization(company)
        account_id = info['accounts'][0].get('account_id')
        base_path = company.ds_base_uri + '/restapi'
        envelope_id = self.disclosure_id.ds_envelope_id

        api_client = ApiClient()
        api_client.host = base_path
        api_client.set_default_header(header_name="Authorization", header_value="Bearer " + self.access_token)

        envelope_api = EnvelopesApi(api_client)
        # Call the envelope get method
        try:
            results = envelope_api.get_envelope(account_id=account_id, envelope_id=envelope_id)
            if results.status == 'completed':
                self.disclosure_id.write({'status': 'signed'})
            self.disclosure_id = False
        except Exception as e:
            raise UserError(
                _("Method doesn't work. Wrong credentials?\n%s" % (e))
            )

        return results

    def get_info(self):
        r = requests.get(
            'https://account-d.docusign.com/oauth/userinfo',
            headers={
                'Authorization': "Bearer %s" % self.access_token,
            },
        )
        info = json.loads(r.text)

        return info


class DocuSignOdooToken(models.Model):
    _name = "docusign.odoo.token"

    code = fields.Char()
