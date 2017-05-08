from openerp import api, models, fields, SUPERUSER_ID

class email_template(models.Model):
    _inherit = "email.template"
    
    def render_template_batch(self, cr, uid, template, model, res_ids, context=None, post_process=False):
        results = super(email_template, self).render_template_batch(cr, uid, template, model, res_ids, context=context, post_process=post_process)
        new_name = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'web_debranding.new_name', False, context)
        new_name = new_name and new_name.strip() or _('Software')
        for res_id in res_ids:
            results[res_id] = results[res_id].replace('Odoo', new_name)
        return results