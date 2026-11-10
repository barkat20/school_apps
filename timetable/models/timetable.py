# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TimeTable(models.Model):
    """Defining model for time table."""

    _description = "Time Table"
    _name = "time.table"

    @api.depends("timetable_ids")
    def _compute_user(self):
        """Method to compute user."""
        for rec in self:
            rec.user_ids = [
                teacher.teacher_id.employee_id.user_id.id
                for teacher in rec.timetable_ids
            ]

    name = fields.Char(string="Description", help="Enter description of timetable")
    standard_id = fields.Many2one(
        "school.standard",
        "Academic Class",
        required=True,
        help="Select Standard",
    )
    year_id = fields.Many2one(
        "academic.year", "Year", required=True, help="Select academic year"
    )
    timetable_ids = fields.One2many(
        "time.table.line",
        "table_id",
        "TimeTable",
        help="Enter the timetable pattern",
    )
    timetable_type = fields.Selection(
        [("regular", "Regular")],
        "Time Table Type",
        default="regular",
        # invisible=True,
        help="Select time table type",
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Users",
        compute="_compute_user",
        store=True,
        help="Teachers following this timetable",
    )
    class_room_id = fields.Many2one(
        "class.room",
        "Room Number",
        help="Class room in which tome table would be followed",
    )

    @api.constrains("year_id", "standard_id")
    def _check_timetable(self):
        for record in self:
            if record.year_id and record.standard_id:
                existing_records = self.search(
                    [
                        ("year_id", "=", record.year_id.id),
                        ("standard_id", "=", record.standard_id.id),
                        ("id", "!=", record.id),  # Exclude the current record
                        ("timetable_type", "=", record.timetable_type),
                    ]
                )
                if existing_records:
                    raise ValidationError(
                        _("A record with the same Year and Standard already exists.")
                    )

    def action_generate_timetable(self):
        """Foundational logic for automatic timetable generation based on Algerian week."""
        self.ensure_one()
        if self.timetable_ids:
            raise ValidationError(_("Timetable already contains lines. Please clear them before generating."))
        
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
        start_time = 8.0
        
        subjects = self.env['subject.subject'].search([('standard_ids', 'in', [self.standard_id.id])])
        if not subjects:
            raise ValidationError(_("No subjects configured for this class."))
            
        lines = []
        day_idx = 0
        current_time = start_time
        
        for subject in subjects:
            teacher = subject.teacher_ids[0] if subject.teacher_ids else False
            if not teacher:
                continue
                
            lines.append((0, 0, {
                'subject_id': subject.id,
                'teacher_id': teacher.id,
                'week_day': days[day_idx],
                'start_time': current_time,
                'end_time': current_time + 1.0,
                'class_room_id': self.class_room_id.id if self.class_room_id else False,
            }))
            
            current_time += 1.0
            if current_time >= 12.0: # Break at noon
                current_time = 8.0
                day_idx = (day_idx + 1) % len(days)
                
        self.write({'timetable_ids': lines})

    @api.constrains("timetable_ids")
    def _check_lecture(self):
        """Method to check same lecture is not assigned on same day."""
        if self.timetable_type == "regular":
            line_ids = self.env["time.table.line"].search(
                [("table_id", "in", self.ids)]
            )
            for rec in line_ids:
                records = [
                    rec_check.id
                    for rec_check in line_ids
                    if (
                        rec.week_day == rec_check.week_day
                        and rec.start_time == rec_check.start_time
                        and rec.end_time == rec_check.end_time
                        and rec.teacher_id.id == rec.teacher_id.id
                    )
                ]
                if len(records) > 1:
                    raise ValidationError(
                        _(
                            f"You cannot set lecture at same time {rec.start_time}"
                            f"at same day {rec.week_day}"
                            f"for teacher {rec.teacher_id.name}.!"
                        )
                    )
                # Checks if time is greater than 24 hours than raise error
                if rec.start_time > 24 or rec.end_time > 24:
                    raise ValidationError(
                        _(
                            """
                                Start and End Time should be less than 24 hours!
                            """
                        )
                    )


class TimeTableLine(models.Model):
    """Defining model for time table."""

    _description = "Time Table Line"
    _name = "time.table.line"
    _rec_name = "table_id"

    @api.constrains("teacher_id", "subject_id")
    def check_teacher(self):
        """Check if lecture is not related to teacher than raise error."""
        for rec in self:
            if (
                rec.teacher_id.id not in rec.subject_id.teacher_ids.ids
                and rec.table_id.timetable_type == "regular"
            ):
                raise ValidationError(
                    _(
                        f"The subject {rec.subject_id.name} is "
                        f"not assigned to teacher {rec.teacher_id.name}."
                    )
                )

    teacher_id = fields.Many2one(
        "school.teacher",
        "Faculty Name",
        help="Select Teacher",
    )
    subject_id = fields.Many2one(
        "subject.subject", "Subject Name", help="Select Subject"
    )
    table_id = fields.Many2one("time.table", "TimeTable")
    start_time = fields.Float(
        required=True,
        help="Time according to timeformat of 24 hours",
    )
    end_time = fields.Float(
        required=True,
        help="Time according to timeformat of 24 hours",
    )
    week_day = fields.Selection(
        [
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        "Week day",
        help="Select weekday for timetable",
    )
    class_room_id = fields.Many2one(
        "class.room",
        "Room Number",
        help="Class room in which time table would be followed",
    )

    @api.constrains("start_time", "end_time")
    def check_time_overlap(self):
        for rec in self:
            if rec.week_day and self.search(
                [
                    "&",
                    "&",
                    ("id", "!=", rec.id),
                    ("table_id", "=", rec.table_id.id),
                    ("week_day", "=", rec.week_day),
                    "|",
                    "&",
                    ("start_time", "<", rec.end_time),
                    ("start_time", ">=", rec.start_time),
                    "&",
                    ("end_time", "<=", rec.end_time),
                    ("end_time", ">", rec.start_time),
                ]
            ):
                raise ValidationError(_("Time should not overlap within the same timetable!"))

    @api.constrains("start_time", "end_time", "teacher_id", "week_day", "class_room_id")
    def _check_global_availability(self):
        for rec in self:
            if not rec.week_day:
                continue
            base_domain = [
                ("id", "!=", rec.id),
                ("week_day", "=", rec.week_day),
                "|", "&", ("start_time", "<", rec.end_time), ("start_time", ">=", rec.start_time),
                "&", ("end_time", "<=", rec.end_time), ("end_time", ">", rec.start_time),
            ]
            
            # ISOLATION: Check overlapping across records
            overlapping = self.search(base_domain)
            for ov in overlapping:
                # Isolate timetables so different draft versions don't crash each other!
                same_reality = False
                if getattr(ov.table_id, 'state', False) == 'validated' and getattr(rec.table_id, 'state', False) == 'validated':
                    same_reality = True
                elif getattr(ov.table_id, 'version_name', False) and getattr(rec.table_id, 'version_name', False) and ov.table_id.version_name == rec.table_id.version_name:
                    same_reality = True
                elif not getattr(ov.table_id, 'version_name', False): # Fallback for old timetables without version_name
                    same_reality = True
                    
                if same_reality:
                    # Check Teacher Availability globally
                    if rec.teacher_id and ov.teacher_id == rec.teacher_id:
                        raise ValidationError(_("Teacher %s is already scheduled during this time on %s.") % (rec.teacher_id.name, rec.week_day))
                    
                    # Check Classroom Availability globally
                    if rec.class_room_id and ov.class_room_id == rec.class_room_id:
                        raise ValidationError(_("Classroom %s is already booked during this time on %s.") % (rec.class_room_id.name, rec.week_day))

    @api.constrains("teacher_id", "class_room_id")
    def check_teacher_room(self):
        """Check available room for teacher."""
        for rec in self:
            for data in self.env["time.table"].search([("id", "!=", rec.table_id.id)]):
                # ISOLATION: Isolate timetables so different draft versions don't crash each other!
                same_reality = False
                if getattr(data, 'state', False) == 'validated' and getattr(rec.table_id, 'state', False) == 'validated':
                    same_reality = True
                elif getattr(data, 'version_name', False) and getattr(rec.table_id, 'version_name', False) and data.version_name == rec.table_id.version_name:
                    same_reality = True
                elif not getattr(data, 'version_name', False): # Fallback for old timetables without version_name
                    same_reality = True
                    
                if not same_reality:
                    continue

                for record in data.timetable_ids:
                    if (
                        data.timetable_type == "regular"
                        and rec.table_id.timetable_type == "regular"
                        and rec.teacher_id == record.teacher_id
                        and rec.week_day == record.week_day
                        and rec.start_time == record.start_time
                    ):
                        raise ValidationError(
                            _("There is a lecture of Lecturer at same time!")
                        )
                    if (
                        data.timetable_type == "regular"
                        and rec.table_id.timetable_type == "regular"
                        and rec.class_room_id
                        and record.class_room_id
                        and rec.class_room_id == record.class_room_id
                        and rec.start_time == record.start_time
                    ):
                        raise ValidationError(_("The room is occupied."))


class SubjectSubject(models.Model):
    _inherit = "subject.subject"

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
    ):
        """Override method to get subject related to teacher."""
        teacher_id = self._context.get("teacher_id")
        if teacher_id:
            for teacher_data in self.env["school.teacher"].browse(teacher_id):
                domain.append(("teacher_ids", "in", [teacher_data.id]))
        return super()._search(
            domain=domain,
            offset=offset,
            limit=limit,
            order=order,
        )

    @api.constrains("minimum_marks")
    def _check_negative_marks(self):
        if self.minimum_marks <= 0:
            raise ValidationError(
                _("The value of minimum marks must be greater than zero")
            )

    @api.constrains("maximum_marks", "minimum_marks")
    def _check_similar_name(self):
        if self.maximum_marks == self.minimum_marks:
            raise ValidationError(
                _("Maximum marks and Minimum marks should be different, Not same")
            )
