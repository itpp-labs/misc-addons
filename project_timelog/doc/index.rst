=================
 Project timelog
=================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

Timer launching.

* Go to the menu ``Project->Task``.
* Create a new subtask by pressing the button ``Edit->Add an item``.
* Press the green button ``play`` to switch on timer for this subtask.
* Press red button ``pause`` to stop the timer.

How to see results

* Go to the menu ``Project ->Timelog`` to section ``My timelog``.
* Press to any timer’s datum (log is result of timer’s work).
* Logs of all users appear in secton ``Timelog`` (only for managers).

The timer’s work.

* Click to first timer to start it. Click again to stop it.
* Click the second timer to open the page with the current task.
* Click the third timer to open Logs page for current day.
* Click the fourth to open Logs page for current week.

Compulsory completion of the task

* Click ``edit`` in current task and put to ``stopline`` date and time. (if timer was launched, it stops after achieving this time).

Uninstallation
==============
* Press the button ``uninstall`` in module ``Project timelog`` from the list of modules.

Note
====

* To use the module, you need to be sure that your odoo instance support longpolling, i.e. Instant Messaging works. Read more about how to use the `longpolling  <https://odoo-development.readthedocs.io/en/latest/admin/longpolling.html>`_
