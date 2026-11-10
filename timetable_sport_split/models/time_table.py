from odoo import models, api

class TimeTable(models.Model):
    _inherit = 'time.table'

    @api.depends('timetable_ids', 'timetable_ids.start_time', 'timetable_ids.end_time', 'timetable_ids.subject_id', 'timetable_ids.teacher_id', 'timetable_ids.class_room_id', 'timetable_ids.primary_subject_id')
    def _compute_matrix_html(self):
        day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "saturday"]
        for record in self:
            if not record.timetable_ids:
                record.matrix_html_view = "<p style='padding: 20px; color: #666; font-style: italic;'>Generate a timetable to view the 2D matrix layout here.</p>"
                continue
            
            # Extract unique time slots across the entire timetable (ignore ghost lines for rows)
            time_slots = sorted(list(set(record.timetable_ids.filtered(lambda l: not l.is_ghost).mapped(lambda l: (l.start_time, l.end_time)))))
            
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
                    lines = record.timetable_ids.filtered(lambda l: l.week_day == day and round(l.start_time, 2) == round(s_time, 2) and not l.is_ghost)
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
                            if getattr(ln, 'pin_level', False) == 'pinned':
                                icon = "📌 "
                                border_style = "border: 2px solid gold;"
                            elif getattr(ln, 'pin_level', False) == 'locked':
                                icon = "🔒 "
                                border_style = "border: 2px solid red;"
                            
                            status_alert = ""
                            if getattr(ln, 'state', False) == 'needs_reschedule':
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
