# Copyright 2015-2017 Ildar Nasyrov <https://it-projects.info/>
# Copyright 2015-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProjectProjectAutostaging(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "autostaging.folder"]


class ProjectTaskTypeAutostaging(models.Model):
    _name = "project.task.type"
    _inherit = ["project.task.type", "autostaging.stage"]
    _card_model = "project.task"
    _card_stage_id = "stage_id"
    autostaging_next_stage = fields.Many2one(
        "project.task.type", string="Autostaging next stage"
    )


class ProjectTaskAutostaging(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "autostaging.card"]
    _field_folder_id = "project_id"
    _field_stage_id = "stage_id"
    _state = "kanban_state"
    autostaging_card_next_stage = fields.Many2one(
        "project.task.type",
        string="Autostaging next stage",
        related="stage_id.autostaging_next_stage",
    )
    _track = {
        "stage_id": {
            "ProjectTaskAutostaging.mt_autostaging": lambda self, cr, uid, obj, ctx=None: ctx
            and ctx.get("autostaging")
        }
    }
