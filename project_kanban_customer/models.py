from openerp import api, models, fields, SUPERUSER_ID

class project_project(models.Model):
    _inherit = 'project.project'

    partner_country_image = fields.Binary('Partner\'s country', related='partner_id.country_id.image')
