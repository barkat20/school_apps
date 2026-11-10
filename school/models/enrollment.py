# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SchoolEnrollment(models.Model):
    """Defining an Academic Enrollment."""

    _name = "school.enrollment"
    _description = "Academic Enrollment"
    _order = "start_date desc"

    student_id = fields.Many2one(
        "student.student",
        "Student",
        required=True,
        ondelete="cascade",
    )
    year_id = fields.Many2one(
        "academic.year",
        "Academic Year",
        required=True,
    )
    grade_id = fields.Many2one(
        "grade.master",
        "Grade",
    )
    standard_id = fields.Many2one(
        "standard.standard",
        "Section",
    )
    class_room_id = fields.Many2one(
        "class.room",
        "Classroom",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("transferred", "Transferred"),
        ],
        "Status",
        default="draft",
        tracking=True,
    )
    start_date = fields.Date("Start Date", required=True, default=fields.Date.today)
    end_date = fields.Date("End Date")
