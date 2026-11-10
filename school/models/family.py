# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SchoolFamily(models.Model):
    """Defining a Family record."""

    _name = "school.family"
    _description = "Family Record"
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        required=True,
        ondelete="cascade",
    )
    father_id = fields.Many2one(
        "school.parent",
        string="Father",
        help="Father's parent record",
    )
    mother_id = fields.Many2one(
        "school.parent",
        string="Mother",
        help="Mother's parent record",
    )
    guardian_id = fields.Many2one(
        "school.parent",
        string="Guardian",
        help="Guardian's parent record",
    )
    billing_contact_id = fields.Many2one(
        "school.parent",
        string="Billing Contact",
        help="Parent to whom invoices are sent",
    )
    default_payer_id = fields.Many2one(
        "school.parent",
        string="Default Payer",
        help="Parent responsible for payment",
    )
    student_ids = fields.One2many(
        "student.student",
        "family_id",
        string="Children",
        help="Children in this family",
    )
