import base64

import requests
import werkzeug

from odoo import SUPERUSER_ID, http
from odoo.exceptions import AccessError
from odoo.http import request

from odoo.addons.mail.controllers.main import MailController
from odoo.addons.web.controllers.main import binary_content

from ..models.image import is_url


class MailControllerExtended(MailController):
    @http.route()
    def avatar(self, res_model, res_id, partner_id):
        headers = [("Content-Type", "image/png")]
        status = 200
        content = "R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="  # default image is one white pixel
        if res_model in request.env:
            try:
                # if the current user has access to the document, get the partner avatar as sudo()
                request.env[res_model].browse(res_id).check_access_rule("read")
                if (
                    partner_id
                    in request.env[res_model]
                    .browse(res_id)
                    .sudo()
                    .exists()
                    .message_ids.mapped("author_id")
                    .ids
                ):
                    status, headers, _content = binary_content(
                        model="res.partner",
                        id=partner_id,
                        field="image_medium",
                        default_mimetype="image/png",
                        env=request.env(user=SUPERUSER_ID),
                    )
                    # binary content return an empty string and not a placeholder if obj[field] is False
                    if _content != "":
                        content = _content
                    if status == 304:
                        return werkzeug.wrappers.Response(status=304)
            except AccessError:
                pass

        if status == 301 and is_url(content):
            r = requests.get(content, timeout=5)
            image_base64 = r.content
        else:
            image_base64 = base64.b64decode(content)

        headers.append(("Content-Length", len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)

        return response
