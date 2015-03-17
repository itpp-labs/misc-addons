from openerp import api, models, fields, SUPERUSER_ID

class project_project(models.Model):
    _inherit = 'project.project'

    partner_country_image = fields.Binary('Partner\'s country flag', related='partner_id.country_id.image')
    partner_country_name = fields.Char('Partner\'s country name', related='partner_id.country_id.name')
