# -*- coding: utf-8 -*-
import sys

from odoo.tools import convert

convert.csv.field_size_limit(sys.maxsize)
