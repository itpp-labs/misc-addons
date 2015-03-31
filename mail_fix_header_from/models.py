import re
from openerp.addons.base.ir import ir_mail_server

ir_mail_server.name_with_email_pattern = re.compile(r'([^<@>]+)\s*<([^ ,<@]+@[^> ,]+)>')
