Web tour extra
==============

Superstructure on phantom tours.

* Fixes issue with running Tour in specific backend page. For example, without this module it's impossible to start Tour from ``/web#id=3&view_type=form&model=res.partner``, the hash will be cleaned and Tour begins from ``/web#`` page.
