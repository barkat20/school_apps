# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SchoolCampus(models.Model):
    _name = "school.campus"
    _description = "School Campus"

    name = fields.Char("Campus Name", required=True)
    code = fields.Char("Campus Code")
    school_id = fields.Many2one("school.school", "School", required=True)
    address = fields.Text("Address")


class SchoolBranch(models.Model):
    _name = "school.branch"
    _description = "School Branch"

    name = fields.Char("Branch Name", required=True)
    code = fields.Char("Branch Code")
    campus_id = fields.Many2one("school.campus", "Campus", required=True)
