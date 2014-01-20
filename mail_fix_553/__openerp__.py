{
    "name" : "Fix error 553",
    "version" : "0.3",
    "author" : "Ivan Yelizariev",
    "category" : "Mail",
    "website" : "https://it-projects.info",
    "description": """Update 'Reply-to' field to catchall value in order to fix problem like that:

    2014-01-18 06:25:56,532 6789 INFO trunk openerp.addons.mail.mail_thread: Routing mail from <MYLOGIN@yandex.ru> to admin@MYDOMAIN.com with Message-Id <49131390026345@web16h.yandex.ru>: direct alias match: (u'res.users', 1, {}, 1, browse_record(mail.alias, 1))
2014-01-18 06:25:57,212 6789 ERROR trunk openerp.addons.base.ir.ir_mail_server: Mail delivery failed via SMTP server 'smtp.yandex.ru'.
SMTPSenderRefused: 553
5.7.1 Sender address rejected: not owned by auth user.
MYLOGIN@yandex.ru
Traceback (most recent call last):
  File "/mnt/files/src/openerp-server/server/openerp/addons/base/ir/ir_mail_server.py", line 465, in send_email
    smtp.sendmail(smtp_from, smtp_to_list, message.as_string())
  File "/usr/lib/python2.7/smtplib.py", line 722, in sendmail
    raise SMTPSenderRefused(code, resp, from_addr)
SMTPSenderRefused: (553, '5.7.1 Sender address rejected: not owned by auth user.', 'MYLOGIN@yandex.ru')

2014-01-18 06:25:57,216 6789 ERROR trunk openerp.addons.mail.mail_mail: failed sending mail.mail 2
Traceback (most recent call last):
  File "/mnt/files/src/openerp-server/addons/mail/mail_mail.py", line 284, in send
    context=context)
  File "/mnt/files/src/openerp-server/server/openerp/addons/base/ir/ir_mail_server.py", line 478, in send_email
    raise MailDeliveryException(_("Mail Delivery Failed"), msg)
MailDeliveryException: (u'Mail Delivery Failed', u"Mail delivery failed via SMTP server 'smtp.yandex.ru'.\nSMTPSenderRefused: 553\n5.7.1 Sender address rejected: not owned by auth user.\nMYLOGIN@yandex.ru")
2014-01-18 06:25:57,223 6789 INFO trunk openerp.addons.fetchmail.fetchmail: fetched/processed 1 email(s) on imap server yandex

    """,
    "depends" : ["base", "mail"],
    #"init_xml" : [],
    #"update_xml" : [],
    #"active": True,
    "installable": True
}
