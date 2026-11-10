from odoo import models

class ReportClassTimetableGridOverride(models.AbstractModel):
    _inherit = "report.timetable_creator.report_class_timetable_grid"

    def _get_timetable_grid(self, timetable_id):
        lines = self.env['time.table.line'].search([
            ('table_id', '=', timetable_id.id),
            ('is_ghost', '=', False)
        ], order='start_time')

        # Find unique time slots
        time_slots = []
        for line in lines:
            slot = (line.start_time, line.end_time)
            if slot not in time_slots:
                time_slots.append(slot)
        
        time_slots.sort(key=lambda x: x[0])

        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        grid = {}
        
        for day in days:
            grid[day] = {}
            for slot in time_slots:
                day_line = lines.filtered(lambda l: l.week_day == day and l.start_time == slot[0] and l.end_time == slot[1])
                if day_line:
                    subject_name = day_line[0].primary_subject_id.name if day_line[0].primary_subject_id else (day_line[0].subject_id.name if day_line[0].subject_id else '')
                    if day_line[0].primary_subject_id:
                        subject_name = f"{subject_name} / {day_line[0].subject_id.name}"
                        
                    teacher_name = day_line[0].teacher_id.name if day_line[0].teacher_id else ''
                    room_name = day_line[0].class_room_id.name if day_line[0].class_room_id else ''
                    
                    cell_text = []
                    if subject_name: cell_text.append(subject_name)
                    if teacher_name: cell_text.append(f"({teacher_name})")
                    if room_name: cell_text.append(f"[{room_name}]")
                    
                    grid[day][slot] = "\n".join(cell_text) if cell_text else ''
                else:
                    grid[day][slot] = ''

        return {
            'time_slots': time_slots,
            'grid': grid,
            'days': days
        }
