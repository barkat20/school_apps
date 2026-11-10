# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TimeTableLine(models.Model):
    _inherit = 'time.table.line'
    
    primary_subject_id = fields.Many2one('subject.subject', string="Primary Subject")

    @api.constrains("start_time", "end_time")
    def check_time_overlap(self):
        """Override the base Odoo overlap constraint to dynamically allow explicitly Synchronized Subjects natively!"""
        for rec in self:
            overlap_recs = self.search([
                ("id", "!=", rec.id),
                ("table_id", "=", rec.table_id.id),
                ("week_day", "=", rec.week_day),
                ("state", "!=", "needs_reschedule"),
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
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"FATAL OVERLAP TRIGGERED! rec: {rec.subject_id.name} ({rec.start_time}-{rec.end_time}) vs ov: {ov.subject_id.name} ({ov.start_time}-{ov.end_time}) in {rec.table_id.name}")
                    logger.error("Dumping ALL lines for this timetable:")
                    all_table_lines = self.search([('table_id', '=', rec.table_id.id)])
                    for l in all_table_lines:
                        logger.error(f" - {l.subject_id.name} on {l.week_day} at {l.start_time}-{l.end_time}")
                    raise ValidationError(_("Time should not overlap!\nConflict detected between '%s' and '%s' physically assigned at the exact same time.") % (rec.subject_id.name, ov.subject_id.name))


    @api.constrains("start_time", "end_time", "teacher_id", "week_day", "class_room_id")
    def _check_global_availability(self):
        """Override base global availability to isolate by version_name and state."""
        for rec in self:
            if not rec.week_day:
                continue
                
            base_domain = [
                ("id", "!=", rec.id),
                ("week_day", "=", rec.week_day),
                "|", "&", ("start_time", "<", rec.end_time), ("start_time", ">=", rec.start_time),
                "&", ("end_time", "<=", rec.end_time), ("end_time", ">", rec.start_time),
            ]
            
            overlapping = self.search(base_domain)
            for ov in overlapping:
                same_reality = False
                if ov.table_id.state == 'validated' and rec.table_id.state == 'validated':
                    same_reality = True
                elif ov.table_id.version_name and rec.table_id.version_name and ov.table_id.version_name == rec.table_id.version_name:
                    same_reality = True
                    
                if same_reality:
                    if rec.teacher_id and ov.teacher_id == rec.teacher_id:
                        is_rec_ghost = getattr(rec, 'is_ghost', False)
                        is_ov_ghost = getattr(ov, 'is_ghost', False)
                        if (is_rec_ghost or is_ov_ghost) and rec.table_id == ov.table_id:
                            pass # Allow a ghost line (supervisor block) to overlap with a real line in the same split/timetable
                        else:
                            raise ValidationError(_("Teacher %s is already scheduled during this time on %s.\nConflict: Rec[ID:%s, Table:%s, Time:%s-%s, Ghost:%s] vs Ov[ID:%s, Table:%s, Time:%s-%s, Ghost:%s]") % (
                                rec.teacher_id.name, rec.week_day,
                                rec.id, rec.table_id.name, rec.start_time, rec.end_time, is_rec_ghost,
                                ov.id, ov.table_id.name, ov.start_time, ov.end_time, is_ov_ghost
                            ))
                    if rec.class_room_id and ov.class_room_id == rec.class_room_id:
                        is_rec_ghost = getattr(rec, 'is_ghost', False)
                        is_ov_ghost = getattr(ov, 'is_ghost', False)
                        if (is_rec_ghost or is_ov_ghost) and rec.table_id == ov.table_id:
                            pass
                        else:
                            raise ValidationError(_("Classroom %s is already booked during this time on %s.") % (rec.class_room_id.name, rec.week_day))

    @api.constrains("teacher_id", "class_room_id")
    def check_teacher_room(self):
        """Check available room for teacher, ignoring unassigned rooms and missing days.
           Also isolates validations to only match within the SAME Version Name, or if both are Validated.
        """
        for rec in self:
            for data in self.env["time.table"].search([("id", "!=", rec.table_id.id)]):
                
                # ISOLATION: 
                # Draft timetables are alternate realities. They should only conflict with themselves.
                same_reality = False
                if data.state == 'validated' and rec.table_id.state == 'validated':
                    same_reality = True
                elif data.version_name and rec.table_id.version_name and data.version_name == rec.table_id.version_name:
                    same_reality = True
                
                if not same_reality:
                    continue

                for record in data.timetable_ids:
                    if (
                        data.timetable_type == "regular"
                        and rec.table_id.timetable_type == "regular"
                        and rec.state != 'needs_reschedule'
                        and record.state != 'needs_reschedule'
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
                        and rec.state != 'needs_reschedule'
                        and record.state != 'needs_reschedule'
                        and rec.class_room_id
                        and record.class_room_id
                        and rec.class_room_id == record.class_room_id
                        and rec.week_day == record.week_day
                        and rec.start_time == record.start_time
                    ):
                        raise ValidationError(_("The room is occupied."))
    state = fields.Selection([
        ('assigned', 'Assigned'),
        ('needs_reschedule', 'Needs Reschedule')
    ], string='Status', default='assigned', required=True)
    
    pin_level = fields.Selection([
        ('normal', 'Normal'),
        ('pinned', 'Pinned'),
        ('locked', 'Locked')
    ], string="Pin Level", default='normal', help="Normal: AI can move. Pinned: AI should not move. Locked: Cannot be modified manually or by AI.")
    
    # Metadata for Forced Assignments
    pinned_by_id = fields.Many2one('res.users', string="Pinned By")
    pinned_date = fields.Datetime(string="Pinned Date")
    pinned_reason = fields.Char(string="Pinned Reason")
    force_level = fields.Selection([
        ('safe', 'Safe'),
        ('soft', 'Soft Conflict'),
        ('hard', 'Hard Conflict'),
        ('impossible', 'Impossible')
    ], string="Conflict Severity")
class TimeTable(models.Model):
    _inherit = 'time.table'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated')
    ], string='Status', default='draft')
    
    version_name = fields.Char(string='Version Name', copy=False)
    academic_stage_id = fields.Many2one('standard.standard', related='standard_id.standard_id', string='Academic Stage', store=True)
    matrix_html_view = fields.Html(string='2D Matrix View', compute='_compute_matrix_html', sanitize=False, sanitize_tags=False, sanitize_attributes=False)

    @api.depends('timetable_ids', 'timetable_ids.start_time', 'timetable_ids.end_time', 'timetable_ids.subject_id', 'timetable_ids.teacher_id', 'timetable_ids.class_room_id')
    def _compute_matrix_html(self):
        day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "saturday"]
        for record in self:
            if not record.timetable_ids:
                record.matrix_html_view = "<p style='padding: 20px; color: #666; font-style: italic;'>Generate a timetable to view the 2D matrix layout here.</p>"
                continue
            
            # Extract unique time slots across the entire timetable
            time_slots = sorted(list(set(record.timetable_ids.mapped(lambda l: (l.start_time, l.end_time)))))
            
            # Construct raw HTML Table structure natively
            html = "<table class='table table-bordered table-striped text-center' style='width: 100%; border: 1px solid #dee2e6; margin-top: 15px; table-layout: fixed;'>"
            html += "<thead class='table-light'><tr><th style='width: 10%; background-color: #f8f9fa; vertical-align: middle;'>Time</th>"
            
            for day in day_names:
                html += f"<th style='width: 15%; background-color: #f8f9fa; vertical-align: middle;'>{day.capitalize()}</th>"
            html += "</tr></thead><tbody>"
            
            for s_time, e_time in time_slots:
                # Intelligently format float times to HH:MM natively
                s_hour = int(s_time)
                s_min = int(round((s_time % 1) * 60))
                e_hour = int(e_time)
                e_min = int(round((e_time % 1) * 60))
                
                time_str = f"{s_hour:02d}:{s_min:02d} - {e_hour:02d}:{e_min:02d}"
                html += f"<tr><td style='font-weight: bold; vertical-align: middle; background-color: #f8f9fa;'>{time_str}</td>"
                
                for day in day_names:
                    lines = record.timetable_ids.filtered(lambda l: l.week_day == day and round(l.start_time, 2) == round(s_time, 2))
                    if not lines:
                        import urllib.parse
                        try:
                            action_id = self.env.ref('timetable_creator.action_open_force_assign_wizard').id
                            ctx = f'{{"default_table_id": {record.id}, "default_day": "{day}", "default_start_time": {s_time}, "default_end_time": {e_time}}}'
                            ctx_str = urllib.parse.quote(ctx)
                            href = f"/web#action={action_id}&model=timetable.force.assign.wizard&target=new&view_type=form&context={ctx_str}"
                            
                            data_attrs = f"data-table-id='{record.id}' data-day='{day}' data-start-time='{s_time}' data-end-time='{e_time}'"
                            if record.state != 'validated':
                                html += f"<td class='force-assign-cell' {data_attrs} style='vertical-align: middle; padding: 10px; background-color: #fcfcfc; cursor: pointer;' onmouseover=\"this.style.backgroundColor='#f0f0f0';\" onmouseout=\"this.style.backgroundColor='#fcfcfc';\">"
                                html += f"<div style='display: block; width: 100%; height: 100%; color: #ccc; font-size: 24px; text-align: center;' title='Force Assign'>+</div>"
                            else:
                                html += f"<td style='vertical-align: middle; padding: 10px; background-color: #fcfcfc;'>"
                            html += "</td>"
                        except Exception as e:
                            html += "<td></td>"
                    else:
                        
                        # User Aesthetic Directive: Fold parallel/synchronized subjects cleanly with slashes natively!
                        cell_content = ""
                        border_style = ""
                        for ln in lines:
                            icon = ""
                            if ln.pin_level == 'pinned':
                                icon = "📌 "
                                border_style = "border: 2px solid gold;"
                            elif ln.pin_level == 'locked':
                                icon = "🔒 "
                                border_style = "border: 2px solid red;"
                            
                            status_alert = ""
                            if ln.state == 'needs_reschedule':
                                status_alert = "<br/><span style='background-color: #ffc107; color: #856404; padding: 2px 4px; border-radius: 3px; font-size: 10px;'>Needs Reschedule</span>"
                                border_style = "border: 2px dashed orange;"

                            subj_name = ln.subject_id.name or '-'
                            if hasattr(ln, 'primary_subject_id') and ln.primary_subject_id:
                                subj_name = f"{ln.primary_subject_id.name} / {subj_name}"
                                
                            teach_name = ln.teacher_id.name or '-'
                            room_name = ln.class_room_id.name or ''
                            
                            cell_content += f"<div style='margin-bottom: 5px;'><strong style='color: #016b80; display: block;'>{icon}{subj_name}</strong><small class='text-muted' style='display: block;'>{teach_name}</small>"
                            if room_name:
                                cell_content += f"<small class='text-muted' style='display: block;'>Rm: {room_name}</small>"
                            cell_content += status_alert + "</div>"
                            
                        import urllib.parse
                        try:
                            action_id = self.env.ref('timetable_creator.action_open_force_assign_wizard').id
                            ctx = f'{{"default_table_id": {record.id}, "default_day": "{day}", "default_start_time": {s_time}, "default_end_time": {e_time}}}'
                            ctx_str = urllib.parse.quote(ctx)
                            href = f"/web#action={action_id}&model=timetable.force.assign.wizard&target=new&view_type=form&context={ctx_str}"
                            data_attrs = f"data-table-id='{record.id}' data-day='{day}' data-start-time='{s_time}' data-end-time='{e_time}'"
                            if record.state != 'validated':
                                html += f"<td class='force-assign-cell' {data_attrs} style='vertical-align: middle; padding: 10px; {border_style} cursor: pointer;' onmouseover=\"this.style.backgroundColor='#f0f0f0';\" onmouseout=\"this.style.backgroundColor='transparent';\">{cell_content}</td>"
                            else:
                                html += f"<td style='vertical-align: middle; padding: 10px; {border_style}'>{cell_content}</td>"
                        except Exception as e:
                            pass
                        
                html += "</tr>"
                
            html += "</tbody></table>"
            record.matrix_html_view = html

    def action_validate(self):
        for rec in self:
            rec.state = 'validated'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.constrains("year_id", "standard_id", "state", "timetable_type")
    def _check_timetable(self):
        """Override Base Constraint to only block if BOTH are validated!"""
        for record in self:
            if record.year_id and record.standard_id and record.state == 'validated':
                existing_records = self.search(
                    [
                        ("year_id", "=", record.year_id.id),
                        ("standard_id", "=", record.standard_id.id),
                        ("id", "!=", record.id),
                        ("timetable_type", "=", record.timetable_type),
                        ("state", "=", "validated"),
                    ]
                )
                if existing_records:
                    raise ValidationError(
                        _("A VALIDATED record with the same Year and Standard already exists.")
                    )

