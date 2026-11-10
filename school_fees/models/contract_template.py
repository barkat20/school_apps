# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SchoolContractTemplate(models.Model):
    _name = "school.contract.template"
    _description = "Contract Template"

    name = fields.Char("Template Name", required=True)
    grade_id = fields.Many2one("grade.master", "Grade")
    line_ids = fields.One2many("school.contract.template.line", "template_id", "Fee Categories")
    installment_plan_id = fields.Many2one("school.installment.plan", "Default Installment Plan")

class SchoolContractTemplateLine(models.Model):
    _name = "school.contract.template.line"
    _description = "Contract Template Line"

    template_id = fields.Many2one("school.contract.template", "Template", required=True, ondelete="cascade")
    category_id = fields.Many2one("school.fee.category", "Fee Category", required=True)
    amount = fields.Float("Amount", required=True)
