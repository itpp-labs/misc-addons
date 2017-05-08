# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class open_acad(models.Model):
#     _name = 'open_acad.open_acad'

#     name = fields.Char()

class Course(models.Model):
    _name = "openacad.course"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    
