=============
 Module Name
=============

The module adds new function to `odoo python tests <https://odoo-development.readthedocs.io/en/latest/dev/tests/python.html>`_::

    phantom_js_multi(sessions, commands, **kw)

* ``sessions`` is dictonary of sessions::

    {"session1": {
       "url_path": "/web"
       "ready": "window",
       "login": "admin",
       "timeout": 10, # page loading timeout
     }
    }

* ``commands`` is a list of commands::

    [{"session": "session1",
      "code": "console.log('ok')",
      "ready": false, # wait before calling next command
      "timeout": 60, # code execution timeout
      }]

* Usual behaviour applies for each code::

    // To signal success test do:
    console.log('ok')
    
    // To signal failure do:
    console.log('error')
    
    // If neither are done before timeout test fails.


Credits
=======

Contributors
------------
* Ivan Yelizariev <yelizariev@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`_

Further information
===================

Installation notes: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 8.0 17a130428516d9dd8105f90e8c9a65a0b4e8901b
