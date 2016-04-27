Extended tours
==============

Extra features for tours:

* Fixes issue with running Tour in specific backend page. For example, without this module it's impossible to start Tour from ``/web#id=3&view_type=form&model=res.partner``, the hash will be cleaned and Tour begins from ``/web#`` page.
    * To launch tutorial using ir.action.todo we need to change url (add some values assignment). To relaunch tour, for example if you uninstall and install it again, you need to change url back (like *database/web*). If url will be same tutorial wount be started.