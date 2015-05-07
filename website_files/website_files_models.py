from openerp import api, models, fields

from openerp.tools import html_escape as escape
import werkzeug


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.one
    def _get_website_file_url(self):
        if self.url:
            url = self.url
        else:
            url = self.env['website'].file_url(self)
        self.website_file_url = url

    @api.one
    def _get_website_file_count(self):
        count = 0
        if self.website_file:
            url = escape(self.website_file_url)
            count = self.env['ir.ui.view'].search_count(
                ["|", ('arch', 'like', '"%s"' % url),
                 ('arch', 'like', "'%s'" % url)])
        self.website_file_count = count

    website_file = fields.Boolean('Website',
                                  help='Attachment available at website')
    website_file_count = fields.Integer('Number of uses',
                                        compute=_get_website_file_count)

    website_file_url = fields.Char('File url', compute=_get_website_file_url)

    def try_remove_file(self, cr, uid, ids, context=None):
        Views = self.pool['ir.ui.view']
        attachments_to_remove = []
        # views blocking removal of the attachment
        removal_blocked_by = {}

        for attachment in self.browse(cr, uid, ids, context=context):
            # in-document URLs are html-escaped, a straight search will not
            # find them
            url = escape(attachment.website_file_url)
            ids = Views.search(cr, uid,
                               ["|", ('arch', 'like', '"%s"' % url),
                                ('arch', 'like', "'%s'" % url)],
                               context=context)

            if ids:
                removal_blocked_by[attachment.id] = Views.read(
                    cr, uid, ids, ['name'], context=context)
            else:
                attachments_to_remove.append(attachment.id)
        if attachments_to_remove:
            self.unlink(cr, uid, attachments_to_remove, context=context)
        return removal_blocked_by

    def check(self, cr, uid, ids, mode, context=None, values=None):
        if ids and mode == 'read':
            if isinstance(ids, (int, long)):
                ids = [ids]
            ids = ids[:]  # make a copy
            cr.execute('SELECT id,website_file FROM ir_attachment WHERE id = ANY (%s)', (ids,))
            for id, website_file in cr.fetchall():
                if website_file:
                    ids.remove(id)
            if not ids:
                return
        return super(ir_attachment, self).check(cr, uid, ids, mode, context, values)


class website(models.Model):
    _inherit = 'website'

    def file_url(self, record, field='datas',
                 filename_field='datas_fname', context=None):
        model = record._name
        #sudo_record = record.sudo()
        #hash_value = hashlib.sha1(sudo_record.write_date or sudo_record.create_date or '').hexdigest()[0:7]
        args = {
            'id': record.id,
            'model': model,
            'filename_field': filename_field,
            'field': field,
            #'hash': hash_value,
        }
        return '/web/binary/saveas?%s' % werkzeug.url_encode(args)

    def search_files(self, cr, uid, ids, needle=None,
                     limit=None, context=None):
        name = (needle or "")
        res = []
        res = self.pool['ir.attachment'].search_read(cr, uid, domain=[
            ('website_file', '=', True),
            '|', ('datas_fname', 'ilike', name), ('name', 'ilike', name)
        ], fields=['datas_fname', 'website_file_url'], limit=limit)
        return res
