from openerp import models, api, fields, exceptions, SUPERUSER_ID


class IRRule(models.Model):
    _inherit = 'ir.rule'

    protected = fields.Boolean('Protected', help='Make rule editable only for superuser')

    @api.multi
    def check_restricted(self):
        if self.env.user.id == SUPERUSER_ID:
            return
        for r in self:
            if r.protected:
                raise exceptions.Warning("The Rule is protected. You don't have access for this operation")

    @api.multi
    def write(self, vals):
        self.check_restricted()
        return super(IRRule, self).write(vals)

    @api.multi
    def unlink(self):
        self.check_restricted()
        return super(IRRule, self).unlink()
