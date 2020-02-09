# pylint: disable=redefined-builtin
import base64

import werkzeug.utils
import werkzeug.wrappers

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import Binary, binary_content


class Controller(Binary):
    @http.route("/web/pdf", type="http", auth="public")
    def content_pdf(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename_field="datas_fname",
        unique=None,
        filename=None,
        mimetype=None,
        download=False,
    ):
        return self.get_media_content(
            xmlid,
            model,
            id,
            field,
            filename_field,
            unique,
            filename,
            mimetype,
            download,
            "application/pdf",
            "pdf",
        )

    @http.route("/web/doc", type="http", auth="public")
    def content_doc(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename_field="datas_fname",
        unique=None,
        filename=None,
        mimetype=None,
        download=False,
    ):
        return self.get_media_content(
            xmlid,
            model,
            id,
            field,
            filename_field,
            unique,
            filename,
            mimetype,
            download,
            "application/msword",
            "doc",
        )

    @http.route("/web/docx", type="http", auth="public")
    def content_docx(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename_field="datas_fname",
        unique=None,
        filename=None,
        mimetype=None,
        download=False,
    ):
        return self.get_media_content(
            xmlid,
            model,
            id,
            field,
            filename_field,
            unique,
            filename,
            mimetype,
            download,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "docx",
        )

    @http.route("/web/xls", type="http", auth="public")
    def content_xls(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename_field="datas_fname",
        unique=None,
        filename=None,
        mimetype=None,
        download=False,
    ):
        return self.get_media_content(
            xmlid,
            model,
            id,
            field,
            filename_field,
            unique,
            filename,
            mimetype,
            download,
            "application/vnd.ms-excel",
            "xls",
        )

    @http.route("/web/xlsx", type="http", auth="public")
    def content_xlsx(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename_field="datas_fname",
        unique=None,
        filename=None,
        mimetype=None,
        download=False,
    ):
        return self.get_media_content(
            xmlid,
            model,
            id,
            field,
            filename_field,
            unique,
            filename,
            mimetype,
            download,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        )

    def get_media_content(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename_field="datas_fname",
        unique=None,
        filename=None,
        mimetype=None,
        download=False,
        default_mimetype=None,
        media_type=None,
    ):
        status, headers, content = binary_content(
            xmlid=xmlid,
            model=model,
            id=id,
            field=field,
            unique=unique,
            filename=filename,
            filename_field=filename_field,
            download=download,
            mimetype=mimetype,
            default_mimetype=default_mimetype,
        )
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(
                (
                    "Content-Disposition",
                    "inline; filename=%s." % str(filename) + media_type,
                )
            )
            response = request.make_response(content_base64, headers)

        response.status_code = status
        return response
