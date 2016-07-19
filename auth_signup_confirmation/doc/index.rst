===============================
 Email confirmation on sign up
===============================

Usage
=====

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`_ this module
* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`_
* Update Confirmation page if needed

  * Open ``Settings / Technical / Parameters / System Parameters``
  * Update value for record ``auth_signup_confirmation.url_singup_thankyou``

* Update Email template if needed

  * Open ``Settings / Technical / Email / Templates``
  * Update Template ``email for registration``

* Sign up

  * Open new Incognito window or simly log out
  * Navigate to ``/web`` page
  * Click ``Sing up`` link
  * Fill out the form
  * Click ``[Sing up]`` button

* Try to login without confirmation - you will get error "Wrong login\password"

* Check email and follow the link - now you can log in
