# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class TimetableTeacherAssignment(models.Model):
    _name = "timetable.teacher.assignment"
    _description = "Teacher Timetable Assignment"
    _rec_name = "teacher_id"

    # Teacher Setup
    teacher_id = fields.Many2one(
        "school.teacher", 
        string="Teacher", 
        required=True
    )
    
    # Hours & Class Lines mapping mapping
    assignment_line_ids = fields.One2many(
        "timetable.teacher.assignment.line",
        "assignment_id",
        string="Classes & Hours Mapping"
    )

class TimetableTeacherAssignmentLine(models.Model):
    _name = "timetable.teacher.assignment.line"
    _description = "Teacher Assignment Line"

    assignment_id = fields.Many2one(
        "timetable.teacher.assignment", 
        string="Assignment Record", 
        ondelete="cascade", 
        required=True
    )
    standard_id = fields.Many2one(
        "school.standard", 
        string="Class", 
        required=True
    )
    group_ids = fields.Many2many(
        "school.class.group", 
        string="Groups",
        domain="[('standard_id', '=', standard_id)]",
        help="Select the specific groups the teacher will teach in this class. If empty, the teacher teaches the whole class."
    )
    subject_id = fields.Many2one(
        "subject.subject",
        string="Subject",
        required=True,
    )
    hours_per_week = fields.Float(
        string="Hours Per Week", 
        required=True,
        default=1.0,
        help="How many hours per week they should teach this specific assignment."
    )

    @api.onchange('standard_id', 'assignment_id')
    def _onchange_standard_id(self):
        for rec in self:
            teacher = rec.assignment_id.teacher_id
            if teacher:
                # 1. Try to find a subject that matches both teacher and standard
                domain = [('teacher_ids', 'in', teacher.id)]
                if rec.standard_id:
                    domain.append(('standard_id', '=', rec.standard_id.id))
                
                subject = self.env['subject.subject'].search(domain, limit=1)
                
                # 2. If no exact match for the standard, just get ANY subject this teacher teaches
                if not subject:
                    subject = self.env['subject.subject'].search([('teacher_ids', 'in', teacher.id)], limit=1)
                    
                if subject:
                    rec.subject_id = subject.id
