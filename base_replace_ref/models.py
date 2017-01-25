# -*- coding: utf-8 -*-
from openerp import api
from openerp import exceptions
from openerp import fields
from openerp import models


class ReplaceRule(models.Model):
    _name = 'base_replace_ref.rule'

    name = fields.Char('Name', required=True)
    draft = fields.Boolean('Draft', default=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True)

    value_line_ids = fields.One2many('base_replace_ref.rule.value_line', 'rule_id', string='Value lines')

    field_line_ids = fields.One2many('base_replace_ref.rule.field_line', 'rule_id', string='Field lines')

    @api.multi
    def find_fields(self):
        for r in self:
            r.find_fields_one()
        return True

    @api.multi
    def find_fields_one(self):
        self.ensure_one()
        if not self.model_id:
            raise exceptions.Warning('Define Model first')

        self.draft = True
        cur_fields = [line.field_id.id for line in self.field_line_ids]
        for field in self.env['ir.model.fields'].search([('relation', '=', self.model_id.model)]):
            if field.id in cur_fields:
                continue
            self.env['base_replace_ref.rule.field_line'].create({'rule_id': self.id, 'model_id': field.model_id.id, 'field_id': field.id})

    @api.multi
    def clear_fields(self):
        for r in self:
            r.clear_fields_one()
        return True

    @api.multi
    def clear_fields_one(self):
        self.ensure_one()
        self.field_line_ids.unlink()

    @api.model
    def parse_value(self, model, value):
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            pass
        res = self.env.ref(value)
        assert res, 'Value not found for ref %s' % value
        return res.id

    @api.multi
    def apply(self):
        for r in self:
            r.apply_one()
        return True

    @api.multi
    def apply_one(self):
        self.ensure_one()
        if self.draft:
            raise exceptions.Warning('You cannot apply draft rule')

        for vline in self.value_line_ids:
            src = self.parse_value(self.model_id.model, vline.src)
            dst = self.parse_value(self.model_id.model, vline.dst)

            for fline in self.field_line_ids:
                self.replace(fline.field_id, src, dst)

    @api.model
    def replace(self, field_id, src, dst):
        model = self.env[field_id.model_id.model]

        if field_id.ttype == 'one2many':
            r = self.env[field_id.relation].browse(src)
            parent_id = getattr(r, field_id.relation_field).id
            r.write({field_id.relation_field: None})
            self.env[field_id.relation].browse(dst).write({field_id.relation_field: parent_id})
            return True
        res = model.search([(field_id.name, '=', src)])
        if field_id.ttype == 'many2one':
            res.write({field_id.name: dst})
        if field_id.ttype == 'many2many':
            res.write({field_id.name: [(3, src, False)]})
            res.write({field_id.name: [(4, dst, False)]})


class ValueLine(models.Model):
    _name = 'base_replace_ref.rule.value_line'

    _src_dst_help = 'ID or Reference'

    rule_id = fields.Many2one('base_replace_ref.rule')
    src = fields.Char('Source', help=_src_dst_help, required=True)
    dst = fields.Char('Destination', help=_src_dst_help)


class FieldLine(models.Model):
    _name = 'base_replace_ref.rule.field_line'

    rule_id = fields.Many2one('base_replace_ref.rule')
    model_id = fields.Many2one('ir.model', string='Model')
    field_id = fields.Many2one('ir.model.fields', string='Field', required=True)
