# Copyright 2015-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2017 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2017 Nicolas JEUDY <https://github.com/njeudy>
# Copyright 2017 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import functools
import io

import odoo
from odoo import http
from odoo.http import request
from odoo.modules import get_module_resource

from odoo.addons.web.controllers import main as controllers_main
from odoo.addons.web.controllers.main import Binary, WebClient

from ..models.ir_translation import debrand, debrand_bytes

db_monodb = http.db_monodb


class BinaryCustom(Binary):
    @http.route(
        ["/web/binary/company_logo", "/logo", "/logo.png"], type="http", auth="none"
    )
    def company_logo(self, dbname=None, **kw):
        imgname = "logo.png"
        default_logo_module = "web_debranding"
        if request.session.db:
            default_logo_module = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("web_debranding.default_logo_module")
            )
        placeholder = functools.partial(
            get_module_resource, default_logo_module, "static", "src", "img"
        )
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                # create an empty registry
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    cr.execute(
                        """SELECT c.logo_web, c.write_date
                                    FROM res_users u
                               LEFT JOIN res_company c
                                      ON c.id = u.company_id
                                   WHERE u.id = %s
                               """,
                        (uid,),
                    )
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = io.BytesIO(base64.b64decode(row[0]))
                        response = http.send_file(
                            image_data, filename=imgname, mtime=row[1]
                        )
                    else:
                        response = http.send_file(placeholder("nologo.png"))
            except Exception:
                response = http.send_file(placeholder(imgname))
        return response


class WebClientCustom(WebClient):
    @http.route("/web/webclient/qweb", type="http", auth="none")
    def qweb(self, mods=None, db=None):
        files = [
            f[0] for f in controllers_main.manifest_glob("qweb", addons=mods, db=db)
        ]
        last_modified = controllers_main.get_last_modified(files)
        if (
            request.httprequest.if_modified_since
            and request.httprequest.if_modified_since >= last_modified
        ):
            return controllers_main.werkzeug.wrappers.Response(status=304)

        content, checksum = controllers_main.concat_xml(files)
        if request.context["lang"] == "en_US":
            # request.env could be not available
            content = debrand_bytes(request.session.db and request.env or None, content)

        return controllers_main.make_conditional(
            request.make_response(content, [("Content-Type", "text/xml")]),
            last_modified,
            checksum,
        )

    @http.route("/web/webclient/translations", type="json", auth="none")
    def translations(self, mods=None, lang=None):
        res = super(WebClientCustom, self).translations(mods, lang)

        for _module_key, module_vals in res["modules"].items():
            for message in module_vals["messages"]:
                message["id"] = debrand(request.env, message["id"])
                message["string"] = debrand(request.env, message["string"])
        return res
