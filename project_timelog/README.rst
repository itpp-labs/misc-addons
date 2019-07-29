==============
 Time Tracker
==============

The timer:


* allows to track the user working time
* helps to control and see the overall working load during a day/week
* generates the corresponding worktime reports

It is a great solution that could be as alternative to Hubstaff or other work time tracker app.

Credits
=======

Contributors
------------
* Dinar Gabbasov <gabbasov@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`_

Script
======

.. code-block:: python

    base_url = obj.env['ir.config_parameter'].get_param('web.base.url')
    url_task = base_url + '/web#id=%s&' % obj.user_id.id + 'model=project.task'
    value1 = url_task
    value2 = obj.create_date
    value3 = obj.task_name
    data = {'value1': value1, 'value2': value2, 'value3': value3}
    url_request = 'https://maker.ifttt.com/trigger/%s/with/key/cCTNCS_cSDRVWPdMoYXPPQ' % event
    obj.get_requests(url_request, data)

Further information
===================

Demo: http://runbot.it-projects.info/demo/misc-addons/8.0

HTML Description: https://apps.odoo.com/apps/modules/8.0/project_timelog/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 8.0 6a1ecef7759dd72d30d23fe1c55966e1a97bac01
