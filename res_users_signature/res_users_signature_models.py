from openerp.osv import fields as old_fields
from openerp import api,models,fields,tools
from openerp.addons.email_template.email_template import mako_template_env
import re
import base64

class res_users(models.Model):
    _inherit = 'res.users'

    signature_id = fields.Many2one('res.users.signature', string='Signature template', help='Keep empty to edit signature manually')
    _columns = {
        'signature': old_fields.html('Signature', sanitize=False)
    }


    @api.one
    @api.onchange('signature_id')
    def render_signature_id(self):
        if not self.signature_id:
            return
        mako = mako_template_env.from_string(tools.ustr(self.signature_id.template))
        html = mako.render({'user':self})
        if html != self.signature:
            self.signature = html

    @api.one
    def write(self, vals):
        res = super(res_users, self).write(vals)
        if any([k in vals for k in ['company_id']]):
            self.render_signature_id()
        return res



class res_users_signature(models.Model):
    _name = 'res.users.signature'

    name = fields.Char('Name')
    comment = fields.Text('Internal note')
    template = fields.Html('Template', sanitize=False, help='''You can use variables:
* ${user.name}
* ${user.function} (job position)
* ${user.partner_id.company_id.name} (company in a partner form)
* ${user.company_id.name} (current company)
* ${user.email}
* ${user.phone}
* ${user.mobile}
* etc. (contact your administrator for further information)

You can use control structures:

% if user.mobile
    Mobile: ${user.mobile}
% endif

''')
    user_ids = fields.One2many('res.users', 'signature_id', string='Users')

    @api.one
    def write(self, vals):
        res = super(res_users_signature, self).write(vals)
        self.action_update_signature()
        return res

    @api.one
    def action_update_signature(self):
        self.user_ids.render_signature_id()

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def write(self, vals):
        res = super(res_partner, self).write(vals)
        if self.user_ids:
            self.user_ids.render_signature_id()
        return res

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def write(self, vals):
        res = super(hr_employee, self).write(vals)
        self.user_id.render_signature_id()
        return res

class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
               attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
               body_alternative=None, subtype_alternative='plain'):
        ftemplate = '__attachment__%s'
        fcounter = 0
        attachments = attachments or []

        pattern = re.compile(r'"data:image/png;base64,[^"]*"')
        pos = 0
        new_body = ''
        while True:
            match = pattern.search(body, pos)
            if not match:
                break
            s = match.start()
            e = match.end()
            data = body[s+len('"data:image/png;base64,'):e-1]
            new_body += body[pos:s]

            fname = ftemplate % fcounter
            fcounter += 1
            attachments.append( (fname, base64.b64decode(data)) )

            new_body += '"cid:%s"' % fname
            pos = e

        new_body += body[pos:]

        return super(ir_mail_server, self).build_email(email_from, email_to, subject, new_body, email_cc, email_bcc, reply_to, attachments, message_id, references, object_id, subtype, headers, body_alternative, subtype_alternative)
