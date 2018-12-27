`1.1.7`
-------

- **Fix**  When a link to a picture that does not have an extension is written in a binary field, its mimetype is not determined, which leads to an "binascii.Error: decoding with base64 codec failed (Error: Incorrect padding)"
- **Improvement:**  The `index_content` field is filled for attachments when a link to a file is written in a binary field.

`1.1.6`
-------

- **Fix**  When the "image_resize_image" function was called, they received the error "binascii.Error: decoding with base64 codec failed (Error: Incorrect padding)", since the value of the binary field is the URL, not the base_64 string.

`1.1.5`
-------

- **Fix:** Product Variant were downloaded on server instead of passing url

`1.1.4`
-------

- **Improvement:** exclude `ir.ui.menu` attachments from eligible to be stored outside (e.g. `ir_attachment_s3`). There is only one small web icon image in this model - no point to store it outside

`1.1.3`
-------

- **FIX:** Error when using `avatar` controller (in `mail` module). For example it is used in `website_project` on `/my/projects` page

`1.1.2`
-------

- **FIX:** Error on saving multiple URLs at once

`1.1.1`
-------

- **FIX:** Ability to use the module for res.partner model
- **FIX:** Images are displayed in kanban view correctly

`1.1.0`
-------

- **NEW:** Specify images URL from interface (e.g. product form) directly

`1.0.0`
-------

- Init version
