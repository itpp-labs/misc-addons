========================
 Project Task Checklist
========================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

Example of usage:
-----------------

* Create User1 and User2 in the ``Settings >> Users`` menu 
* Login as User1 
  
  * Go to ``Project >> Project >> Tasks`` and open the ``Checklist`` tab
  * Create new subtask (Reviewer - User1, Assigned to - User2)

* Login as User2 

  * See message in Inbox like "TODO: subtask_name"
  * Change state of subtask to Cancelled/Done
  * You can see a message in Inbox "Cancelled: subtask_name" or "Done: subtask_name" accordingly. 

* You can see your TODOs on tasks in kanban view in the ``Project >> Project >> Tasks`` menu
* The ``Project >> Project >> Checklist`` menu displays ALL subtasks in state TODO assigned to you and subtasks where you are Reviewer

