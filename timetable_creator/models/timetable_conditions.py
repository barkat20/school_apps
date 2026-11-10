# See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class TimetableClassCondition(models.Model):
    _name = "timetable.class.condition"
    _description = "Global Class Condition"

    name = fields.Char(string="Name", required=True, default="Global Class Limits")
    study_days = fields.Selection(
        [
            ("1", "Monday"),
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday"),
            ("7", "Sunday"),
        ],
        string="Study Days",
    )
    day_sunday = fields.Boolean(string="Sunday", default=True)
    day_monday = fields.Boolean(string="Monday", default=True)
    day_tuesday = fields.Boolean(string="Tuesday", default=True)
    day_wednesday = fields.Boolean(string="Wednesday", default=True)
    day_thursday = fields.Boolean(string="Thursday", default=True)
    day_friday = fields.Boolean(string="Friday", default=False)
    day_saturday = fields.Boolean(string="Saturday", default=False)

    # Sunday TIME LIMITS
    sunday_study_morning = fields.Boolean(string="Sunday Morning Classes", default=True)
    sunday_start_morning = fields.Float(string="Sunday Start Morning", default=8.0)
    sunday_end_morning = fields.Float(string="Sunday End Morning", default=12.0)
    sunday_study_evening = fields.Boolean(string="Sunday Evening Classes", default=True)
    sunday_start_evening = fields.Float(string="Sunday Start Evening", default=13.0)
    sunday_end_evening = fields.Float(string="Sunday End Evening", default=15.0)

    # Monday TIME LIMITS
    monday_study_morning = fields.Boolean(string="Monday Morning Classes", default=True)
    monday_start_morning = fields.Float(string="Monday Start Morning", default=8.0)
    monday_end_morning = fields.Float(string="Monday End Morning", default=12.0)
    monday_study_evening = fields.Boolean(string="Monday Evening Classes", default=True)
    monday_start_evening = fields.Float(string="Monday Start Evening", default=13.0)
    monday_end_evening = fields.Float(string="Monday End Evening", default=15.0)

    # Tuesday TIME LIMITS
    tuesday_study_morning = fields.Boolean(string="Tuesday Morning Classes", default=True)
    tuesday_start_morning = fields.Float(string="Tuesday Start Morning", default=8.0)
    tuesday_end_morning = fields.Float(string="Tuesday End Morning", default=12.0)
    tuesday_study_evening = fields.Boolean(string="Tuesday Evening Classes", default=True)
    tuesday_start_evening = fields.Float(string="Tuesday Start Evening", default=13.0)
    tuesday_end_evening = fields.Float(string="Tuesday End Evening", default=15.0)

    # Wednesday TIME LIMITS
    wednesday_study_morning = fields.Boolean(string="Wednesday Morning Classes", default=True)
    wednesday_start_morning = fields.Float(string="Wednesday Start Morning", default=8.0)
    wednesday_end_morning = fields.Float(string="Wednesday End Morning", default=12.0)
    wednesday_study_evening = fields.Boolean(string="Wednesday Evening Classes", default=True)
    wednesday_start_evening = fields.Float(string="Wednesday Start Evening", default=13.0)
    wednesday_end_evening = fields.Float(string="Wednesday End Evening", default=15.0)

    # Thursday TIME LIMITS
    thursday_study_morning = fields.Boolean(string="Thursday Morning Classes", default=True)
    thursday_start_morning = fields.Float(string="Thursday Start Morning", default=8.0)
    thursday_end_morning = fields.Float(string="Thursday End Morning", default=12.0)
    thursday_study_evening = fields.Boolean(string="Thursday Evening Classes", default=True)
    thursday_start_evening = fields.Float(string="Thursday Start Evening", default=13.0)
    thursday_end_evening = fields.Float(string="Thursday End Evening", default=15.0)

    # Friday TIME LIMITS
    friday_study_morning = fields.Boolean(string="Friday Morning Classes", default=True)
    friday_start_morning = fields.Float(string="Friday Start Morning", default=8.0)
    friday_end_morning = fields.Float(string="Friday End Morning", default=12.0)
    friday_study_evening = fields.Boolean(string="Friday Evening Classes", default=True)
    friday_start_evening = fields.Float(string="Friday Start Evening", default=13.0)
    friday_end_evening = fields.Float(string="Friday End Evening", default=15.0)

    # Saturday TIME LIMITS
    saturday_study_morning = fields.Boolean(string="Saturday Morning Classes", default=True)
    saturday_start_morning = fields.Float(string="Saturday Start Morning", default=8.0)
    saturday_end_morning = fields.Float(string="Saturday End Morning", default=12.0)
    saturday_study_evening = fields.Boolean(string="Saturday Evening Classes", default=True)
    saturday_start_evening = fields.Float(string="Saturday Start Evening", default=13.0)
    saturday_end_evening = fields.Float(string="Saturday End Evening", default=15.0)

class TimetableTeacherGlobalCondition(models.Model):
    _name = "timetable.teacher.global.condition"
    _description = "Global Teacher Condition"

    name = fields.Char(string="Name", default="Global Teacher Limits")
    min_hours_per_day = fields.Float(string="Min Hours Per Day", default=2.0)
    max_hours_per_day = fields.Float(string="Max Hours Per Day", default=6.0)
    mandatory_free_days_count = fields.Integer(string="Mandatory Free Days per week", default=1)
    allowed_gaps = fields.Integer(string="Allowed Gaps per week", default=0)


class TimetableTeacherSpecificCondition(models.Model):
    _name = "timetable.teacher.specific.condition"
    _description = "Specific Teacher Condition"

    teacher_id = fields.Many2one("school.teacher", string="Teacher", required=True)
    
    # Specific Free Days
    has_specific_free_days = fields.Boolean(string="Has specific free days")
    free_day_monday = fields.Boolean("Free Monday")
    free_day_tuesday = fields.Boolean("Free Tuesday")
    free_day_wednesday = fields.Boolean("Free Wednesday")
    free_day_thursday = fields.Boolean("Free Thursday")
    free_day_friday = fields.Boolean("Free Friday")
    free_day_saturday = fields.Boolean("Free Saturday")
    free_day_sunday = fields.Boolean("Free Sunday")

    # Custom Time Windows
    has_custom_time_window = fields.Boolean(string="Has Custom Time Window")
    
    # Sunday
    sunday_morning = fields.Boolean(string="Sunday Morning", default=True)
    sunday_morning_start = fields.Float(string="Start", default=8.0)
    sunday_morning_end = fields.Float(string="End", default=12.0)
    sunday_evening = fields.Boolean(string="Sunday Evening", default=True)
    sunday_evening_start = fields.Float(string="Start", default=13.0)
    sunday_evening_end = fields.Float(string="End", default=17.0)

    # Monday
    monday_morning = fields.Boolean(string="Monday Morning", default=True)
    monday_morning_start = fields.Float(string="Start", default=8.0)
    monday_morning_end = fields.Float(string="End", default=12.0)
    monday_evening = fields.Boolean(string="Monday Evening", default=True)
    monday_evening_start = fields.Float(string="Start", default=13.0)
    monday_evening_end = fields.Float(string="End", default=17.0)

    # Tuesday
    tuesday_morning = fields.Boolean(string="Tuesday Morning", default=True)
    tuesday_morning_start = fields.Float(string="Start", default=8.0)
    tuesday_morning_end = fields.Float(string="End", default=12.0)
    tuesday_evening = fields.Boolean(string="Tuesday Evening", default=True)
    tuesday_evening_start = fields.Float(string="Start", default=13.0)
    tuesday_evening_end = fields.Float(string="End", default=17.0)

    # Wednesday
    wednesday_morning = fields.Boolean(string="Wednesday Morning", default=True)
    wednesday_morning_start = fields.Float(string="Start", default=8.0)
    wednesday_morning_end = fields.Float(string="End", default=12.0)
    wednesday_evening = fields.Boolean(string="Wednesday Evening", default=True)
    wednesday_evening_start = fields.Float(string="Start", default=13.0)
    wednesday_evening_end = fields.Float(string="End", default=17.0)

    # Thursday
    thursday_morning = fields.Boolean(string="Thursday Morning", default=True)
    thursday_morning_start = fields.Float(string="Start", default=8.0)
    thursday_morning_end = fields.Float(string="End", default=12.0)
    thursday_evening = fields.Boolean(string="Thursday Evening", default=True)
    thursday_evening_start = fields.Float(string="Start", default=13.0)
    thursday_evening_end = fields.Float(string="End", default=17.0)

    # Friday
    friday_morning = fields.Boolean(string="Friday Morning", default=True)
    friday_morning_start = fields.Float(string="Start", default=8.0)
    friday_morning_end = fields.Float(string="End", default=12.0)
    friday_evening = fields.Boolean(string="Friday Evening", default=True)
    friday_evening_start = fields.Float(string="Start", default=13.0)
    friday_evening_end = fields.Float(string="End", default=17.0)

    # Saturday
    saturday_morning = fields.Boolean(string="Saturday Morning", default=True)
    saturday_morning_start = fields.Float(string="Start", default=8.0)
    saturday_morning_end = fields.Float(string="End", default=12.0)
    saturday_evening = fields.Boolean(string="Saturday Evening", default=True)
    saturday_evening_start = fields.Float(string="Start", default=13.0)
    saturday_evening_end = fields.Float(string="End", default=17.0)
