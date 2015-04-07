Force move attachments to a new storage type
============================================

In odoo the type of storage is taken from parameter
**ir_attachment.location**. This module move all attachments to a new
storage type (**db** or **file**) everytime you edit or create the parameter via Settings\Parameters\System Parameters menu.

The module just calls built-in force_storage method of ir.attachment model, so it should be safe enough.

Tested on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625
