# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AuthorizedPickup(models.Model):
    """Defining an Authorized Pickup Person."""

    _name = "school.authorized.pickup"
    _description = "Authorized Pickup Person"

    student_id = fields.Many2one(
        "student.student",
        "Student",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char("Name", required=True)
    relation = fields.Char("Relationship", required=True)
    phone = fields.Char("Phone Number")
    national_id = fields.Char("National ID (NIN/CIN)")
    photo = fields.Binary("Photo")
    can_pick_up = fields.Boolean("Can Pick Up", default=True)
    notes = fields.Text("Notes")
