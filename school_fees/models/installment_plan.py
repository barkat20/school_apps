# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SchoolInstallmentPlan(models.Model):
    _name = "school.installment.plan"
    _description = "Installment Plan"

    name = fields.Char("Plan Name", required=True)
    line_ids = fields.One2many("school.installment.plan.line", "plan_id", "Installments")

    @api.constrains('line_ids')
    def _check_percentages(self):
        for plan in self:
            if plan.line_ids:
                total = sum(line.percentage for line in plan.line_ids)
                if round(total, 2) != 100.0:
                    raise ValidationError("The total percentage of installments must equal 100%.")

class SchoolInstallmentPlanLine(models.Model):
    _name = "school.installment.plan.line"
    _description = "Installment Plan Line"
    _order = "sequence"

    plan_id = fields.Many2one("school.installment.plan", "Plan", required=True, ondelete="cascade")
    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence", default=10)
    percentage = fields.Float("Percentage (%)", required=True)
    days_from_start = fields.Integer("Days from Contract Start", help="When this installment is due")
