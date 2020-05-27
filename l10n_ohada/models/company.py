# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = "res.company"

#    check_transfer_account_id = fields.Many2one('account.account', ondelete='restrict',
#        domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id), ('deprecated', '=', False)], 
#        string="Compte de transfert de chèques", help="Compte intermédiaire pour le transfert de chèques.")
#    check_transfer_post_move = fields.Boolean(string='Validation automatique', help="Valider les écritures comptables automatiquement")
