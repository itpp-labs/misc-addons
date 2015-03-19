Fix mail error 553
==================

Module updates 'FROM' field to portal@MYDOMAIN.COM  value in order to fix 553 error on a mail service that checks FROM field.

E.g:

* Customer send email from USER@CUSTOMER.com to info@MYDOMAIN.COM
* odoo accept email and try to send notifcation to related odoo users. E.g to admin@gmail.com.
* By default odoo prepare notification email with parameters as follows:

  * FROM: user@CUSTOMER.com
  * TO: admin@gmail.com

if you mail service provider, e.g. pdd.yandex.ru, doesn't allow emails with a FROM value differ from ...@MYDOMAIN.COM, then you get 553. This is why you need to update FROM value to portal@MYDOMAIN.COM

You can configure default alias at Settings -> System Parameters -> mail.catchall.alias_from

Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
