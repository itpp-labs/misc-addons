from odoo import models, tools, api, fields


# class MajorUnitProductReport(models.Model):
#     _inherit = "report.major_unit.product_line"

#     @api.model_cr
#     def init(self):
#         tools.drop_view_if_exists(self._cr, 'report_major_unit_product')
#         self._cr.execute("""
#             CREATE VIEW report_major_unit_product AS (
#             SELECT
#                 ro_product.product_id as product_id,
#                 ro.major_unit_id as major_unit_id,
#                 ro_product.id as id,
#                 SUM(ro_product.quantity) as quantity
#             FROM
#                 service_repair_order_product as ro_product
#             LEFT JOIN
#                 service_repair_order as ro ON ro.id = ro_product.repair_order_id
#             GROUP BY
#                 product_id,
#                 major_unit_id,
#                 ro_product.id
#         )
#         """)
