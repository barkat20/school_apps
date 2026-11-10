from odoo import models, fields, api

class TimeTableLine(models.Model):
    _inherit = 'time.table.line'

    primary_subject_id = fields.Many2one(
        "subject.subject",
        string="Primary Subject",
        help="Main subject (like Sport) when split into secondary actual subjects."
    )
    is_ghost = fields.Boolean(default=False, string='Ghost Line', help='Hidden from Class Timetable but visible on Teacher Timetable')

    @api.constrains("start_time", "end_time")
    def check_time_overlap(self):
        """Override the base Odoo overlap constraint to dynamically allow explicitly Synchronized Subjects natively!
           AND ignore ghost lines for the sport split!"""
        from odoo.exceptions import ValidationError
        from odoo import _
        
        for rec in self:
            if rec.is_ghost:
                continue
                
            overlap_recs = self.search([
                ("id", "!=", rec.id),
                ("table_id", "=", rec.table_id.id),
                ("week_day", "=", rec.week_day),
                ("state", "!=", "needs_reschedule"),
                ("is_ghost", "=", False), # IGNORE GHOST LINES
                "|", "|", "|",
                "&", ("start_time", "<=", rec.start_time), ("end_time", ">", rec.start_time),
                "&", ("start_time", "<", rec.end_time), ("end_time", ">", rec.end_time),
                "&", ("start_time", "<", rec.start_time), ("end_time", ">", rec.end_time),
                "&", ("start_time", ">", rec.start_time), ("end_time", "<", rec.end_time),
            ])
            
            for ov in overlap_recs:
                my_rules = self.env['timetable.module.rule'].search([
                    ('subject_id', '=', rec.subject_id.id),
                    '|', ('academic_stage_id', '=', rec.table_id.standard_id.standard_id.id), ('academic_stage_id', '=', False)
                ])
                
                ov_rules = self.env['timetable.module.rule'].search([
                    ('subject_id', '=', ov.subject_id.id),
                    '|', ('academic_stage_id', '=', ov.table_id.standard_id.standard_id.id), ('academic_stage_id', '=', False)
                ])
                
                my_allows = any(r.is_synchronized and ov.subject_id.id in r.synchronized_subject_ids.ids for r in my_rules)
                ov_allows = any(r.is_synchronized and rec.subject_id.id in r.synchronized_subject_ids.ids for r in ov_rules)
                
                if not (my_allows or ov_allows):
                    raise ValidationError(_("Time should not overlap!\nConflict detected between '%s' and '%s' physically assigned at the exact same time.") % (rec.subject_id.name, ov.subject_id.name))
