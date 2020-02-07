# Copyright 2014 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, make_msgid

import html2text
from bs4 import BeautifulSoup

from odoo import api, fields, models, tools
from odoo.loglevels import ustr

from odoo.addons.base.models.ir_mail_server import (
    encode_header,
    encode_header_param,
    encode_rfc2822_address_header,
)

try:
    from odoo.addons.mail.models.mail_template import mako_template_env
except ImportError:
    pass


VALID_TAGS = ["p", "img"]


def sanitize_html(value):

    soup = BeautifulSoup(value, "lxml").html.body

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.extract()

    return soup.renderContents().decode()


class ResUsers(models.Model):
    _inherit = "res.users"
    signature_id = fields.Many2one(
        "res.users.signature",
        string="Signature template",
        help="Keep empty to edit signature manually",
    )
    signature = fields.Html("Signature", sanitize=True)

    @api.onchange("signature_id")
    def render_signature_id(self):
        if not self.signature_id:
            return
        mako = mako_template_env.from_string(tools.ustr(self.signature_id.template))
        html = mako.render({"user": self})
        if html != self.signature:
            self.signature = html

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        for r in self:
            if any(
                [
                    k in vals
                    for k in ["signature_id", "company_id", "name", "phone", "email"]
                ]
            ):
                r.render_signature_id()
        return res


class ResUsersSignature(models.Model):
    _name = "res.users.signature"
    _description = "Users signatures"

    name = fields.Char("Name")
    comment = fields.Text("Internal note")
    template = fields.Html(
        "Template",
        sanitize=True,
        help="""You can use variables:
* ${user.name}
* ${user.function} (job position)
* ${user.partner_id.company_id.name} (company in a partner form)p
* ${user.company_id.name} (current company)
* ${user.email}
* ${user.phone}
* ${user.mobile}
* etc. (contact your administrator for further information)

You can use control structures:

% if user.mobile
    Mobile: ${user.mobile}
% endif

""",
    )
    user_ids = fields.One2many("res.users", "signature_id", string="Users")

    @api.multi
    def write(self, vals):
        if "template" in vals:
            vals["template"] = sanitize_html(vals["template"])
        res = super(ResUsersSignature, self).write(vals)
        for r in self:
            r.action_update_signature()
        return res

    @api.multi
    def action_update_signature(self):
        for r in self:
            if r.user_ids:
                for i in r.user_ids.ids:
                    r.user_ids.browse(i).render_signature_id()
        return True


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for r in self:
            if r.user_ids:
                r.user_ids.render_signature_id()
        return res


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def build_email(
        self,
        email_from,
        email_to,
        subject,
        body,
        email_cc=None,
        email_bcc=None,
        reply_to=False,
        attachments=None,
        message_id=None,
        references=None,
        object_id=False,
        subtype="plain",
        headers=None,
        body_alternative=None,
        subtype_alternative="plain",
    ):
        """ copy-pasted from odoo/addons/base/models/ir_mail_server.py::build_email """

        ftemplate = "__image-%s__"
        fcounter = 0
        attachments = attachments or []

        pattern = re.compile(r'"data:image/png;base64,[^"]*"')
        pos = 0
        new_body = ""
        body = body or ""
        while True:
            match = pattern.search(body, pos)
            if not match:
                break
            s = match.start()
            e = match.end()
            data = body[s + len('"data:image/png;base64,') : e - 1]
            new_body += body[pos:s]
            fname = ftemplate % fcounter
            fcounter += 1
            attachments.append((fname, base64.b64decode(data)))

            new_body += '"cid:%s"' % fname
            pos = e

        new_body += body[pos:]
        body = new_body

        email_from = email_from or tools.config.get("email_from")
        assert email_from, (
            "You must either provide a sender address explicitly or configure "
            "a global sender address in the server configuration or with the "
            "--email-from startup parameter."
        )

        # Note: we must force all strings to to 8-bit utf-8 when crafting message,
        #       or use encode_header() for headers, which does it automatically.

        headers = headers or {}  # need valid dict later

        if not email_cc:
            email_cc = []
        if not email_bcc:
            email_bcc = []
        if not body:
            body = u""

        email_body_utf8 = ustr(body).encode("utf-8")
        email_text_part = MIMEText(email_body_utf8, _subtype=subtype, _charset="utf-8")
        msg = MIMEMultipart()

        if not message_id:
            if object_id:
                message_id = tools.generate_tracking_message_id(object_id)
            else:
                message_id = make_msgid()
        msg["Message-Id"] = encode_header(message_id)
        if references:
            msg["references"] = encode_header(references)
        msg["Subject"] = encode_header(subject)
        msg["From"] = encode_rfc2822_address_header(email_from)
        del msg["Reply-To"]
        if reply_to:
            msg["Reply-To"] = encode_rfc2822_address_header(reply_to)
        else:
            msg["Reply-To"] = msg["From"]
        msg["To"] = encode_rfc2822_address_header(COMMASPACE.join(email_to))
        if email_cc:
            msg["Cc"] = encode_rfc2822_address_header(COMMASPACE.join(email_cc))
        if email_bcc:
            msg["Bcc"] = encode_rfc2822_address_header(COMMASPACE.join(email_bcc))
        msg["Date"] = formatdate()
        # Custom headers may override normal headers or provide additional ones
        for key, value in headers.items():
            msg[ustr(key).encode("utf-8")] = encode_header(value)

        if subtype == "html" and not body_alternative and html2text:
            # Always provide alternative text body ourselves if possible.
            text_utf8 = tools.html2text(email_body_utf8.decode("utf-8")).encode("utf-8")
            alternative_part = MIMEMultipart(_subtype="alternative")
            alternative_part.attach(
                MIMEText(text_utf8, _charset="utf-8", _subtype="plain")
            )
            alternative_part.attach(email_text_part)
            msg.attach(alternative_part)
        elif body_alternative:
            # Include both alternatives, as specified, within a multipart/alternative part
            alternative_part = MIMEMultipart(_subtype="alternative")
            body_alternative_utf8 = ustr(body_alternative).encode("utf-8")
            alternative_body_part = MIMEText(
                body_alternative_utf8, _subtype=subtype_alternative, _charset="utf-8"
            )
            alternative_part.attach(alternative_body_part)
            alternative_part.attach(email_text_part)
            msg.attach(alternative_part)
        else:
            msg.attach(email_text_part)

        if attachments:
            for (fname, fcontent) in attachments:
                filename_rfc2047 = encode_header_param(fname)
                part = MIMEBase("application", "octet-stream")

                # The default RFC2231 encoding of Message.add_header() works in Thunderbird but not GMail
                # so we fix it by using RFC2047 encoding for the filename instead.
                part.sudo().set_param("name", filename_rfc2047)
                part.add_header(
                    "Content-Disposition", "attachment", filename=filename_rfc2047
                )
                part.add_header("Content-ID", "<%s>" % filename_rfc2047)  # NEW STUFF

                part.set_payload(fcontent)
                encoders.encode_base64(part)
                msg.attach(part)
        return msg
