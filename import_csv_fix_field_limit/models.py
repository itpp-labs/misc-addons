# -*- coding: utf-8 -*-
import sys
from openerp.tools import convert
convert.csv.field_size_limit(sys.maxsize)
