from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TimetableForceAssignMissing(models.TransientModel):
    _name = 'timetable.force.assign.missing'
    _description = 'Missing Subject Recommender Line'

    wizard_id = fields.Many2one('timetable.force.assign.wizard', required=True, ondelete='cascade')
    subject_id = fields.Many2one('subject.subject', string='Subject')
    standard_id = fields.Many2one('school.standard', string='Class')
    teacher_id = fields.Many2one('school.teacher', string='Teacher')
    suggested_room_id = fields.Many2one('class.room', string='Suggested Room')
    missing_hours = fields.Float(string='Missing Hrs')
    teacher_availability = fields.Char(string='Teacher Status')
    reason = fields.Text(string='Failure Reason')
    status_color = fields.Char(string='Color', default='black')

    def action_assign_this_subject(self):
        self.ensure_one()
        self.wizard_id.subject_id = self.subject_id
        self.wizard_id.teacher_id = self.teacher_id
        # Trigger the assignment
        return self.wizard_id.action_force_pin()

class TimetableForceAssignWizard(models.TransientModel):
    _name = 'timetable.force.assign.wizard'
    _description = 'Force Assign Timetable Slot'

    table_id = fields.Many2one('time.table', string='Timetable', required=True)
    day = fields.Selection([
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday')
    ], string='Day', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    
    is_advanced_override = fields.Boolean(string='Advanced Manual Override', default=False)
    subject_id = fields.Many2one('subject.subject', string='Subject')
    teacher_id = fields.Many2one('school.teacher', string='Teacher')
    missing_subject_ids = fields.One2many('timetable.force.assign.missing', 'wizard_id', string='Missing Subjects')
    
    reason = fields.Char(string='Reason', required=True, help='Reason for forcing this assignment.')
    pin_level = fields.Selection([
        ('pinned', 'Pinned'),
        ('locked', 'Locked')
    ], string='Pin Level', default='pinned', required=True)

    conflict_severity = fields.Selection([
        ('safe', 'Safe 🟢'),
        ('soft', 'Soft Conflict 🟡'),
        ('hard', 'Hard Conflict 🟠'),
        ('impossible', 'Impossible 🔴')
    ], string='Conflict Severity', compute='_compute_conflict', store=False)
    
    conflict_preview_html = fields.Html(string='Conflict Preview', compute='_compute_conflict', store=False)

    @api.depends('teacher_id', 'day', 'start_time')
    @api.onchange('table_id', 'day', 'start_time', 'end_time')
    def _compute_missing_subjects(self):
        for wiz in self:
            wiz.missing_subject_ids = [(5, 0, 0)]
            if not wiz.table_id or not wiz.table_id.standard_id or not wiz.day or wiz.start_time == 0.0:
                continue

            standard = wiz.table_id.standard_id
            
            # Find all teacher assignments for this standard
            # The hours_per_week in the assignment defines the curriculum needed!
            assignment_lines = self.env['timetable.teacher.assignment.line'].search([
                ('standard_id', '=', standard.id)
            ])
            
            missing_lines = []
            for line in assignment_lines:
                subject = line.subject_id
                teacher = line.assignment_id.teacher_id
                
                # Check assigned hours in the timetable for this specific subject and teacher
                assigned_hours = sum(self.env['time.table.line'].search([
                    ('table_id', '=', wiz.table_id.id),
                    ('subject_id', '=', subject.id),
                    ('teacher_id', '=', teacher.id),
                    ('state', '!=', 'needs_reschedule')
                ]).mapped(lambda l: l.end_time - l.start_time))
                
                missing_hrs = line.hours_per_week - assigned_hours
                if missing_hrs > 0:
                    # Check teacher availability
                    same_time_class = self.env['time.table.line'].search([
                        ('teacher_id', '=', teacher.id),
                        ('week_day', '=', wiz.day),
                        ('start_time', '<', wiz.end_time),
                        ('end_time', '>', wiz.start_time),
                        ('state', '!=', 'needs_reschedule'),
                        '|',
                        ('table_id.version_name', '=', wiz.table_id.version_name),
                        ('table_id.state', '=', 'validated')
                    ], limit=1)
                    
                    if same_time_class:
                        avail = f"Teaching {same_time_class[0].table_id.standard_id.name}"
                        color = 'red'
                        reason = f"Teacher is already scheduled to teach {same_time_class[0].table_id.standard_id.name} at this time."
                    else:
                        avail = "Available"
                        color = 'green'
                        reason = "Teacher is available. The algorithm likely skipped this to prevent exceeding daily constraints, or to balance student hours."
                        
                        # Check teacher daily max
                        if hasattr(teacher, 'specific_condition') and teacher.specific_condition:
                            daily_hrs = sum(self.env['time.table.line'].search([
                                ('teacher_id', '=', teacher.id),
                                ('week_day', '=', wiz.day),
                                ('state', '!=', 'needs_reschedule')
                            ]).mapped(lambda l: l.end_time - l.start_time))
                            if daily_hrs >= teacher.specific_condition.max_hours_per_day:
                                reason = f"Teacher has reached their maximum daily limit of {teacher.specific_condition.max_hours_per_day} hours."
                                color = 'orange'
                                
                        # Check if it was because of student daily max
                        std_daily = sum(self.env['time.table.line'].search([
                            ('table_id', '=', wiz.table_id.id),
                            ('week_day', '=', wiz.day),
                            ('state', '!=', 'needs_reschedule')
                        ]).mapped(lambda l: l.end_time - l.start_time))
                        if std_daily >= 6.0: # Assuming 6 hours is typical daily max
                            reason = f"Class already has {std_daily} hours of lessons today. Adding more would exceed daily limits."
                            color = 'orange'
                            
                else:
                    avail = "Fully Scheduled"
                    color = 'gray'
                    reason = ""
                            
                missing_lines.append((0, 0, {
                    'subject_id': subject.id,
                    'standard_id': standard.id,
                    'teacher_id': teacher.id,
                    'missing_hours': missing_hrs,
                    'teacher_availability': avail,
                    'status_color': color,
                    'reason': reason
                }))
            
            # Sort missing_lines so that subjects with actual missing hours appear at the top
            missing_lines.sort(key=lambda x: x[2]['missing_hours'], reverse=True)
            wiz.missing_subject_ids = missing_lines

    def _compute_conflict(self):
        for wiz in self:
            if not wiz.teacher_id or not wiz.day or wiz.start_time == 0.0:
                wiz.conflict_severity = False
                wiz.conflict_preview_html = ""
                continue
                
            # Check for hard conflicts: Is the teacher teaching another class at this exact time?
            # We must check the same version or validated state!
            same_reality_domain = [
                ('teacher_id', '=', wiz.teacher_id.id),
                ('week_day', '=', wiz.day),
                ('start_time', '=', wiz.start_time),
                ('state', '!=', 'needs_reschedule'),
                '|',
                ('table_id.version_name', '=', wiz.table_id.version_name),
                ('table_id.state', '=', 'validated')
            ]
            conflicts = self.env['time.table.line'].search(same_reality_domain)
            
            html = "<div>"
            html += f"<h5>Action Preview</h5>"
            html += f"<div style='border: 1px solid #28a745; padding: 10px; margin-bottom: 10px; border-radius: 5px;'>"
            html += f"<span style='color: #28a745; font-weight: bold;'>✓ Will Create:</span><br/>"
            html += f"<b>{wiz.table_id.standard_id.name}</b> | {wiz.subject_id.name} | {wiz.day.capitalize()} {int(wiz.start_time)}:00 | Teacher {wiz.teacher_id.name} | <b>{wiz.pin_level.capitalize()}</b>"
            html += f"</div>"

            if conflicts:
                wiz.conflict_severity = 'hard'
                html += f"<div style='border: 1px solid #dc3545; padding: 10px; border-radius: 5px;'>"
                html += f"<span style='color: #dc3545; font-weight: bold;'>⚠ Will Remove & Set to 'Needs Reschedule':</span><br/>"
                for c in conflicts:
                    html += f"<b>{c.table_id.standard_id.name}</b> | {c.subject_id.name} | {c.week_day.capitalize()} {int(c.start_time)}:00 | Teacher {c.teacher_id.name}<br/>"
                html += f"</div>"
            else:
                # Check soft conflict: Teacher hours
                teacher_cond = self.env['timetable.teacher.specific.condition'].search([('teacher_id', '=', wiz.teacher_id.id)], limit=1)
                max_hours = teacher_cond.max_hours_per_day if teacher_cond else 6.0
                
                day_hours = sum(self.env['time.table.line'].search([
                    ('teacher_id', '=', wiz.teacher_id.id),
                    ('week_day', '=', wiz.day),
                    ('state', '!=', 'needs_reschedule'),
                    ('table_id.version_name', '=', wiz.table_id.version_name)
                ]).mapped(lambda l: l.end_time - l.start_time))
                
                if day_hours + (wiz.end_time - wiz.start_time) > max_hours:
                    wiz.conflict_severity = 'soft'
                    html += f"<div style='border: 1px solid #ffc107; padding: 10px; border-radius: 5px;'>"
                    html += f"<span style='color: #856404; font-weight: bold;'>🟡 Soft Conflict:</span><br/>"
                    html += f"Teacher {wiz.teacher_id.name} will exceed their preferred maximum of {max_hours} hours on {wiz.day.capitalize()}."
                    html += f"</div>"
                else:
                    wiz.conflict_severity = 'safe'
                    html += f"<div style='border: 1px solid #17a2b8; padding: 10px; border-radius: 5px;'>"
                    html += f"<span style='color: #17a2b8; font-weight: bold;'>🟢 Safe:</span><br/>"
                    html += f"No conflicts detected."
                    html += f"</div>"

            html += "</div>"
            wiz.conflict_preview_html = html

    def action_force_pin(self):
        self.ensure_one()
        
        # Log undo (Simple implementation for now)
        
        # 1. Remove hard conflicts by setting them to 'needs_reschedule'
        same_reality_domain = [
            ('teacher_id', '=', self.teacher_id.id),
            ('week_day', '=', self.day),
            ('start_time', '=', self.start_time),
            ('state', '!=', 'needs_reschedule'),
            '|',
            ('table_id.version_name', '=', self.table_id.version_name),
            ('table_id.state', '=', 'validated')
        ]
        conflicts = self.env['time.table.line'].search(same_reality_domain)
        if conflicts:
            conflicts.write({
                'state': 'needs_reschedule',
                'start_time': 0,
                'end_time': 0,
                'week_day': False,
                'class_room_id': False
            })

        # 2. Assign the new one
        existing_reschedule = self.env['time.table.line'].search([
            ('table_id', '=', self.table_id.id),
            ('subject_id', '=', self.subject_id.id),
            ('state', '=', 'needs_reschedule')
        ], limit=1)
        
        vals = {
            'table_id': self.table_id.id,
            'teacher_id': self.teacher_id.id,
            'subject_id': self.subject_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'week_day': self.day,
            'state': 'assigned',
            'pin_level': self.pin_level,
            'pinned_by_id': self.env.user.id,
            'pinned_date': fields.Datetime.now(),
            'pinned_reason': self.reason,
            'force_level': self.conflict_severity.split(' ')[0] if self.conflict_severity else 'safe'
        }
        
        if existing_reschedule:
            existing_reschedule.write(vals)
        else:
            self.env['time.table.line'].create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
