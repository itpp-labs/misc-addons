Force move attachments to DB storage
====================================

In odoo the type of storage is taken from parameter
**ir_attachment.location**. This module move all attachments to a new
storage type (**db** or **file**) everytime you edit or create the parameter via Settings\\Parameters\\System Parameters menu.

Right after installing **ir_attachment.location** is set to **db**.

To rollback everything, before uninstalling the module set  **ir_attachment.location** to **file**.

Technical implementation
------------------------

The module just calls built-in force_storage method of ir.attachment model, so it should be safe enough.

Note
----
Be carefull about using Database storage on low memory servers.


Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
