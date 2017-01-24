# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp import models
from openerp import tools
from openerp.osv import fields as old_fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _columns = {
        'notify_email': old_fields.selection([
            ('none', 'Never'),
            ('im', 'Only IM (if online)'),
            ('im_xor_email', 'IM (if online) + email (if offline)'),
            ('im_and_email', 'IM (if online) + email'),
            ('always', 'Only emails'),
        ], 'Receive Inbox Notifications by Email, IM', required=True,
            oldname='notification_email_send',
            help="Policy to receive emails, IM for new messages pushed to your personal Inbox. IM can be used only for partners with odoo user account"
        ),
    }


class MailNotification(models.Model):
    _inherit = 'mail.notification'

    def get_recipients(self, cr, uid, ids, message, context=None):
        # based on addons/mail/mail_followers.py::get_partners_to_email
        """ Return the list of partners to notify, based on their preferences.

            :param browse_record message: mail.message to notify
            :param list partners_to_notify: optional list of partner ids restricting
                the notifications to process
        """
        email_pids = []
        im_uids = []
        for notification in self.browse(cr, uid, ids, context=context):
            if notification.is_read:
                continue
            partner = notification.partner_id
            # Do not send to partners without email address defined
            if not partner.email:
                continue
            # Do not send to partners having same email address than the author (can cause loops or bounce effect due to messy database)
            if message.author_id and message.author_id.email == partner.email:
                continue
            # Partner does not want to receive any emails or is opt-out
            n = partner.notify_email
            if n == 'none':
                continue
            if n == 'always':
                email_pids.append(partner.id)
                continue
            send_email = False
            for user in partner.user_ids:
                if user.im_status == 'offline':
                    if n != 'im':
                        send_email = True
                else:
                    im_uids.append(user.id)
                    if n == 'im_and_email':
                        send_email = True

            if not len(partner.user_ids):
                # send notification to partner, that doesn't have odoo account, but has "im*" value in notify_email
                send_email = True

            if send_email:
                email_pids.append(partner.id)

        return email_pids, im_uids

    def _message2im(self, cr, uid, message):
        inbox_action = self.pool['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, 'mail.mail_inboxfeeds')
        inbox_url = '#menu_id=%s' % inbox_action
        url = None
        if message.res_id:
            url = '#id=%s&model=%s&view_type=form' % (
                message.res_id,
                message.model
            )
        author = message.author_id and message.author_id.name_get()
        author = author and author[0][1] or message.email_from

        about = message.subject or message.record_name or 'UNDEFINED'
        about = '[ABOUT] %s' % about
        if url:
            about = '<a href="%s">%s</a>' % (url, about)
        im_text = [
            '_____________________',
            '<a href="%s">_____[open_inbox]_____</a>' % inbox_url,
            '%s [FROM] %s' % (message.type, author),
            about,
        ]
        # im_text = im_text + body.split('\n')
        return im_text

    def _notify_email(self, cr, uid, ids, message_id, force_send=False, user_signature=True, context=None):
        # based on addons/mail/mail_followers.py::_notify_email
        message = self.pool['mail.message'].browse(cr, SUPERUSER_ID, message_id, context=context)

        # compute partners
        email_pids, im_uids = self.get_recipients(cr, uid, ids, message, context=None)
        if email_pids:
            self._do_notify_email(cr, uid, email_pids, message, force_send, user_signature, context)

        if im_uids:
            self._do_notify_im(cr, uid, im_uids, message, context)

        return True

    def _do_notify_im(self, cr, uid, im_uids, message, context=None):
        im_text = self._message2im(cr, uid, message)

        user_from = self.pool['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, 'im_notif.notif_user')

        session_obj = self.pool['im_chat.session']
        message_type = 'message'
        for user_to in im_uids:
            session = session_obj.session_get(cr, user_from, user_to, context=context)
            uuid = session.get('uuid')
            message_content = '\n'.join(im_text)
            self.pool["im_chat.message"].post(cr, SUPERUSER_ID, user_from, uuid, message_type, message_content, context=context)

        return True

    def _do_notify_email(self, cr, uid, email_pids, message, force_send=False, user_signature=True, context=None):

        # compute email body (signature, company data)
        body_html = message.body
        # add user signature except for mail groups, where users are usually adding their own signatures already
        user_id = message.author_id and message.author_id.user_ids and message.author_id.user_ids[0] and message.author_id.user_ids[0].id or None
        signature_company = self.get_signature_footer(cr, uid, user_id, res_model=message.model, res_id=message.res_id, context=context, user_signature=(user_signature and message.model != 'mail.group'))
        if signature_company:
            body_html = tools.append_content_to_html(body_html, signature_company, plaintext=False, container_tag='div')
        # compute email references
        references = message.parent_id.message_id if message.parent_id else False

        # custom values
        custom_values = dict()
        if message.model and message.res_id and self.pool.get(message.model) and hasattr(self.pool[message.model], 'message_get_email_values'):
            custom_values = self.pool[message.model].message_get_email_values(cr, uid, message.res_id, message, context=context)

        # create email values
        max_recipients = 50
        chunks = [email_pids[x:x + max_recipients] for x in xrange(0, len(email_pids), max_recipients)]
        email_ids = []
        for chunk in chunks:
            mail_values = {
                'mail_message_id': message.id,
                'auto_delete': True,
                'body_html': body_html,
                'recipient_ids': [(4, id) for id in chunk],
                'references': references,
            }
            mail_values.update(custom_values)
            email_ids.append(self.pool.get('mail.mail').create(cr, uid, mail_values, context=context))
        if force_send and len(chunks) < 2:  # for more than 50 followers, use the queue system
            self.pool.get('mail.mail').send(cr, uid, email_ids, context=context)
        return True
