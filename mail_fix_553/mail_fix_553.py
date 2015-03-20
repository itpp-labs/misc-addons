# -*- coding: utf-8 -*-

import base64
import logging
from email.utils import formataddr
from urlparse import urljoin

from openerp import api, tools
from openerp import SUPERUSER_ID
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mail_mail(osv.Model):
    _inherit = "mail.mail"

    def send(self, cr, uid, ids, auto_commit=False, raise_exception=False, context=None):
        # copy-paste from addons/mail/mail_mail.py
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :return: True
        """

        # NEW STUFF
        catchall_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.alias_from", context=context)
        catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain", context=context)

        correct_email_from = '@%s>?\s*$'%catchall_domain
        default_email_from = '%s@%s' % (catchall_alias, catchall_domain)


        context = dict(context or {})
        ir_mail_server = self.pool.get('ir.mail_server')
        ir_attachment = self.pool['ir.attachment']
        for mail in self.browse(cr, SUPERUSER_ID, ids, context=context):
            try:
                # TDE note: remove me when model_id field is present on mail.message - done here to avoid doing it multiple times in the sub method
                if mail.model:
                    model_id = self.pool['ir.model'].search(cr, SUPERUSER_ID, [('model', '=', mail.model)], context=context)[0]
                    model = self.pool['ir.model'].browse(cr, SUPERUSER_ID, model_id, context=context)
                else:
                    model = None
                if model:
                    context['model_name'] = model.name

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachment_ids = [a.id for a in mail.attachment_ids]
                attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
                                 for a in ir_attachment.read(cr, SUPERUSER_ID, attachment_ids,
                                                             ['datas_fname', 'datas'])]

                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(self.send_get_email_dict(cr, uid, mail, context=context))
                for partner in mail.recipient_ids:
                    email_list.append(self.send_get_email_dict(cr, uid, mail, partner=partner, context=context))
                # headers
                headers = {}
                bounce_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.bounce.alias", context=context)
                catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain", context=context)
                if bounce_alias and catchall_domain:
                    if mail.model and mail.res_id:
                        headers['Return-Path'] = '%s-%d-%s-%d@%s' % (bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
                    else:
                        headers['Return-Path'] = '%s-%d@%s' % (bounce_alias, mail.id, catchall_domain)
                if mail.headers:
                    try:
                        headers.update(eval(mail.headers))
                    except Exception:
                        pass

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({'state': 'exception'})
                mail_sent = False

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:

                    # NEW STUFF
                    email_from = mail.email_from
                    if re.search(correct_email_from, email_from) is None:
                        email_from = default_email_from

                    msg = ir_mail_server.build_email(
                        email_from=email_from, # NEW STUFF
                        email_to=email.get('email_to'),
                        subject=email.get('subject'),
                        body=email.get('body'),
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(mail.email_cc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    try:
                        res = ir_mail_server.send_email(cr, uid, msg,
                                                    mail_server_id=mail.mail_server_id.id,
                                                    context=context)
                    except AssertionError as error:
                        if error.message == ir_mail_server.NO_VALID_RECIPIENT:
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.warning("Ignoring invalid recipients for mail.mail %s: %s",
                                            mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:
                    mail.write({'state': 'sent', 'message_id': res})
                    mail_sent = True

                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                if mail_sent:
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                self._postprocess_sent_message(cr, uid, mail, context=context, mail_sent=mail_sent)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception('MemoryError while processing mail with ID %r and Msg-Id %r. '\
                                      'Consider raising the --limit-memory-hard startup option',
                                  mail.id, mail.message_id)
                raise
            except Exception as e:
                _logger.exception('failed sending mail.mail %s', mail.id)
                mail.write({'state': 'exception'})
                self._postprocess_sent_message(cr, uid, mail, context=context, mail_sent=False)
                if raise_exception:
                    if isinstance(e, AssertionError):
                        # get the args of the original error, wrap into a value and throw a MailDeliveryException
                        # that is an except_orm, with name and value as arguments
                        value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                cr.commit()
        return True


        for mail in self.browse(cr, SUPERUSER_ID, ids, context=context):
            email_from = mail.email_from
            if not email_from or re.search(correct_email_from, email_from) is None:
                mail.write({'email_from': default_email_from})
        return super(mail_mail, self).send(cr, uid, ids, context=context, **kwargs)
