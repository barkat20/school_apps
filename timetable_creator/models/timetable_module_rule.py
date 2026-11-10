# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class TimetableModuleRule(models.Model):
    _name = "timetable.module.rule"
    _description = "Module Rule"
    _rec_name = "subject_id"

    @api.model
    def _setup_base(self):
        super()._setup_base()
        import logging
        logging.error("DEBUG_SETUP_BASE: timetable.module.rule IS BEING SETUP!")

    # Module Identity
    subject_id = fields.Many2one(
        "subject.subject", 
        string="Subject (Module)", 
        required=True
    )

    # Stage / Group specificity
    academic_stage_id = fields.Many2one(
        "standard.standard",
        string="Academic Stage",
        help="The Academic Stage (e.g., Middle School) this rule applies to. Applies to all classes in this stage."
    )
    group_ids = fields.Many2many(
        "school.class.group",
        string="Groups Teaching this Module",
        domain="[('standard_id.standard_id', '=', academic_stage_id)]",
        help="Select the specific groups studying this module, filtered by the selected Academic Stage."
    )

    # Hour details
    hours_per_week = fields.Float(
        string="Hours Per Week", 
        default=2.0, 
        required=True,
        help="How many hours per week these groups study this module."
    )
    hours_per_session = fields.Float(
        string="Hours Per Session (Block)",
        default=1.0,
        help="E.g. If set to 2.0, this module will be scheduled as a single 2-hour consecutive block."
    )
    allow_multiple_sessions_per_day = fields.Boolean(
        string="Allow Multiple Sessions Per Day",
        default=False,
        help="Check this to allow scheduling this subject more than once on the same day (e.g. Arabic, Math, etc.)."
    )

    # Synchronization logic
    is_synchronized = fields.Boolean(
        string="Is Synchronized (Parallel Subjects)",
        help="Check this if this module studies at the exact same time as another module."
    )
    synchronized_subject_ids = fields.Many2many(
        "subject.subject", 
        string="Synchronized Subjects",
        help="E.g. If Group 1 studies Science, Group 2 MUST study these subjects at the same time."
    )

    # Phase 1 Features
    required_room_type_id = fields.Many2one(
        "class.room.type",
        string="Required Room Type",
        help="If set, this subject can only be scheduled in classrooms of this type (e.g., PC Lab)."
    )
    min_days_between = fields.Integer(
        string="Minimum Days Between Sessions",
        default=0,
        help="To prevent heavy subjects from being taught on consecutive days. 1 means at least 1 day gap."
    )
