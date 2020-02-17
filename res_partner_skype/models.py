# Copyright 2014-2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2017 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2017 ArtyomLosev <https://github.com/ArtyomLosev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    skype = fields.Char("Skype", size=128, index=True)
