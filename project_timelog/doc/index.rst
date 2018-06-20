=================
 Project timelog
=================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* To use the module, you need to be sure that your odoo instance support longpolling, i.e. Instant Messaging works. Read more about how to use the `longpolling  <https://odoo-development.readthedocs.io/en/latest/admin/longpolling.html>`_
* You need to install a patch to use the new group (the beginning of the week is Sunday). The use of the patch is optional and needed only to use Sunday grouping (otherwise only Monday works). More `here. <https://github.com/odoo/odoo/pull/25086>`__ To apply the patch execute::

    cd /path/to/odoo/source
    patch -p1 < /path/to/0001-IMP-support-grouping-by-weeks-starting-with-Sunday.patch

Usage
=====

Timer launching

* Go to the menu ``Project >> Task``.
* Create a new subtask by clicking on ``Edit >> Add an item``.
* Click on green button ``play`` to switch on timer for this subtask.
* Click on red button ``pause`` to stop the timer.

How to see results

* Go to the menu ``Project >> Timelog >> My timelog``.
* Press to any timer’s datum (log is result of timer’s work).
* Logs of all users appear in secton ``Timelog`` (only for managers).

The timer work

* Click on the first timer to start it. Click again to stop it.
* Click on the second timer to open the page with the current task.
* Click on the third timer to open Logs page for current day.
* Click on the fourth timer to open Logs page for current week.

Forced completion of the task

* Click on ``Edit`` in current task and put to ``stopline`` date and time (if the timer was launched, it stops after achieving this time).

Uninstallation
==============
* Open the``Project timelog`` module by going to Apps and click on the ``Uninstall`` button.
