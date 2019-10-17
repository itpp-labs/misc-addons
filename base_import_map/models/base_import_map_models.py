from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class Import(models.TransientModel):
    _inherit = "base_import.import"

    def get_map(self, options):
        if options.get('settings'):
            settings = self.env["base_import_map.map"].search([("id", "=", options.get('settings'))])
            return settings

    def parse_preview(self, options, count=10):
        res = super(Import, self).parse_preview(options, count=10)
        settings = self.get_map(options)
        if settings:
            res['matches'] = {r.column_number: [str(r.field_name)] for r in settings.line_ids}
        return res

    def do(self, fields, options, dryrun=False):
        res = super(Import, self).do(fields, options, dryrun=dryrun)
        if not dryrun and options['save_settings']:
            model_id = self.env["ir.model"].search([("model", "=", str(self.res_model))]).id
            new_settings = self.env["base_import_map.map"].create({
                "name": str(options['save_settings']),
                "model_id": model_id,
                "file_read_hook": options['file_read_hook'],
            })
            settings_line = self.env["base_import_map.line"]
            k = 0
            for field in fields:
                if field:
                    settings_line.create({
                        "setting_id": new_settings.id,
                        "field_name": field,
                        "column_number": k

                    })
                k += 1
        return res

    def _read_file(self, options):
        res = super(Import, self)._read_file(options)
        get_hook = self.get_map(options)

        if get_hook:
            file_read_hook = get_hook.file_read_hook
        else:
            file_read_hook = options["file_read_hook"]

        if not file_read_hook:
            return res

        def f(row):
            safe_eval(file_read_hook, {}, {'row': row}, mode="exec", nocopy=True)
            return row

        return (f(row) for row in res)


class SettingImport(models.Model):
    _name = "base_import_map.map"

    name = fields.Char(string="Setting Name")
    file_read_hook = fields.Text(string="File read hook", help="""
Update values of the file. Use variable ``row`` to update values in a row.""")
    model_id = fields.Many2one("ir.model", string="Models")
    model = fields.Char(related="model_id.model", store=True)
    line_ids = fields.One2many("base_import_map.line", "setting_id", string="Settings line")


class SettingLineImport(models.Model):
    _name = "base_import_map.line"
    _order = "column_number"

    setting_id = fields.Many2one(
        "base_import_map.map", string="Settings",
        required=True, ondelete='cascade', index=True)
    field_name = fields.Char(string="Name")
    column_number = fields.Integer(string="Column number")
