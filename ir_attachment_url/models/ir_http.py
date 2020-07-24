# Copyright 2016-2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2017 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import werkzeug

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _find_field_attachment(cls, env, m, f, res_id):
        domain = [
            ("res_model", "=", m),
            ("res_field", "=", f),
            ("res_id", "=", res_id),
            ("type", "=", "binary"),
            ("url", "!=", False),
        ]
        return (
            env["ir.attachment"]
            .sudo()
            .search_read(domain=domain, fields=["url", "mimetype", "checksum"], limit=1)
        )

    @classmethod
    def find_field_attachment(cls, env, model, field, obj):
        is_attachment = env[model]._fields[field].attachment
        if not is_attachment:
            return env["ir.attachment"]

        related = env[model]._fields[field].related
        if related and len(related) >= 2:
            related_obj = obj[related[0]]
            att = cls._find_field_attachment(
                env, related_obj._name, related[1], related_obj.id
            )
        else:
            att = cls._find_field_attachment(env, model, field, obj.id)

        return att

    def _binary_record_content(self, record, **kw):
        model = record._name
        field = kw.get("field", "datas")

        filename = kw.get("filename")
        mimetype = "mimetype" in record and record.mimetype or False
        content = None
        filehash = "checksum" in record and record["checksum"] or False

        field_def = record._fields[field]
        if field_def.type == "binary" and field_def.attachment:
            field_attachment = self.find_field_attachment(
                self.env, model, field, record
            )
            if field_attachment:
                mimetype = field_attachment[0]["mimetype"]
                content = field_attachment[0]["url"]
                filehash = field_attachment[0]["checksum"]
                return 302, content, filename, mimetype, filehash

        return super(IrHttp, self)._binary_record_content(record, **kw)

    def _response_by_status(self, status, headers, content):
        if status == 302:
            return werkzeug.utils.redirect(content, code=302)
        return super(IrHttp, self)._response_by_status(status, headers, content)
