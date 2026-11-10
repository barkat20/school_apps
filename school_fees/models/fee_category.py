# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SchoolFeeCategory(models.Model):
    _name = "school.fee.category"
    _description = "School Fee Category"

    name = fields.Char("Category Name", required=True)
    code = fields.Char("Code", required=True)
    product_id = fields.Many2one("product.product", "Related Product", required=True)
    description = fields.Text("Description")
