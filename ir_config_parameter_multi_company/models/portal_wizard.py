# -*- coding: utf-8 -*-

from odoo.exceptions import UserError

from odoo import api, models


class PortalWizardUser(models.TransientModel):
    """
        A model to configure users in the portal wizard for current website in current company.
    """

    _inherit = 'portal.wizard.user'

    @api.multi
    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        """ From selected partners, add corresponding users to chosen portal group. It either granted
            existing user, or create new one (and add it to the group) for current website in current company.
        """
        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))

        # Change: website_id is necessary in context for a company with multi website.
        # The wizard create an access for current website in current company
        for wizard_user in self.sudo().with_context(active_test=False, website_id=self.env.user.backend_website_id.id):
            group_portal = wizard_user.wizard_id.portal_id
            if not group_portal.is_portal:
                raise UserError(_('Group %s is not a portal') % group_portal.name)
            user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
            # update partner email, if a new one was introduced
            if wizard_user.partner_id.email != wizard_user.email:
                wizard_user.partner_id.write({'email': wizard_user.email})
            # add portal group to relative user of selected partners
            if wizard_user.in_portal:
                user_portal = None
                # create a user if necessary, and make sure it is in the portal group
                if not user:
                    if wizard_user.partner_id.company_id:
                        company_id = wizard_user.partner_id.company_id.id
                    else:
                        company_id = self.env['res.company']._company_default_get('res.users').id
                    user_portal = wizard_user.sudo().with_context(company_id=company_id)._create_user()
                else:
                    user_portal = user
                wizard_user.write({'user_id': user_portal.id})
                if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                    wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                    # prepare for the signup process
                    wizard_user.user_id.partner_id.signup_prepare()
                    wizard_user.with_context(active_test=True)._send_email()
                wizard_user.refresh()
            else:
                # remove the user (if it exists) from the portal group
                if user and group_portal in user.groups_id:
                    # if user belongs to portal only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal.id)]})
