# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SchoolDiscountPolicy(models.Model):
    _name = "school.discount.policy"
    _description = "Discount Policy"

    name = fields.Char("Policy Name", required=True)
    code = fields.Char("Code")
    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Discount Type", required=True, default='percentage')
    amount = fields.Float("Amount/Percentage", required=True)
    description = fields.Text("Description")
