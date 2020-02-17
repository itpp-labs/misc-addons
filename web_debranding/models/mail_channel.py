# Copyright 2018 Bikbov Rafis <https://it-projects.info/team/bikbov>
# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, models


class Channel(models.Model):
    _inherit = "mail.channel"

    @api.model
    def init_odoobot(self):
        channel = super(Channel, self).init_odoobot()
        if not channel:
            return
        channel.write({"name": "Bot"})
        return channel
