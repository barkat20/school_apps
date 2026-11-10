# See LICENSE file for full copyright and licensing details.

from odoo import api, models

class ReportClassTimetableGrid(models.AbstractModel):
    _name = "report.timetable_creator.report_class_timetable_grid"
    _description = "Class Timetable Grid Report"

    def _get_timetable_grid(self, timetable_id):
        """Generates a Day x Time grid for a class timetable."""
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
        
        # Sort time slots chronologically
        time_slots.sort(key=lambda x: x[0])

        # NEW: Starts on Sunday
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        grid = {}
        
        for day in days:
            grid[day] = {}
            for slot in time_slots:
                # Find line for this day and exact slot block
                day_line = lines.filtered(lambda l: l.week_day == day and l.start_time == slot[0] and l.end_time == slot[1])
                if day_line:
                    subject_name = day_line[0].subject_id.name if day_line[0].subject_id else ''
                    if hasattr(day_line[0], 'primary_subject_id') and day_line[0].primary_subject_id:
                        subject_name = f"{day_line[0].primary_subject_id.name} / {subject_name}"
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

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["time.table"].browse(docids)
        return {
            "doc_ids": docids,
            "docs": docs,
            "doc_model": "time.table",
            "get_timetable_grid": self._get_timetable_grid,
        }


class ReportTeacherTimetableGrid(models.AbstractModel):
    _name = "report.timetable_creator.report_teacher_timetable_grid"
    _description = "Teacher Timetable Grid Report"

    def _get_timetable_grid(self, teacher_id):
        """Generates a Day x Time grid for a teacher's schedule across all tables."""
        lines = self.env['time.table.line'].search([
            ('teacher_id', '=', teacher_id.id),
            ('is_ghost', '=', False)
        ], order='start_time')

        # Find unique time slots
        time_slots = []
        for line in lines:
            slot = (line.start_time, line.end_time)
            if slot not in time_slots:
                time_slots.append(slot)
        
        time_slots.sort(key=lambda x: x[0])

        # NEW: Starts on Sunday
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        grid = {}
        
        for day in days:
            grid[day] = {}
            for slot in time_slots:
                day_line = lines.filtered(lambda l: l.week_day == day and l.start_time == slot[0] and l.end_time == slot[1])
                if day_line:
                    class_name = day_line[0].table_id.standard_id.standard_id.name if day_line[0].table_id.standard_id else ''
                    subject_name = day_line[0].subject_id.name if day_line[0].subject_id else ''
                    if hasattr(day_line[0], 'primary_subject_id') and day_line[0].primary_subject_id:
                        subject_name = f"{day_line[0].primary_subject_id.name} / {subject_name}"
                    room_name = day_line[0].class_room_id.name if day_line[0].class_room_id else ''
                    
                    cell_text = []
                    if class_name: cell_text.append(f"Class: {class_name}")
                    if subject_name: cell_text.append(subject_name)
                    if room_name: cell_text.append(f"[{room_name}]")
                    
                    grid[day][slot] = "\n".join(cell_text) if cell_text else ''
                else:
                    grid[day][slot] = ''

        return {
            'time_slots': time_slots,
            'grid': grid,
            'days': days
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["school.teacher"].browse(docids)
        return {
            "doc_ids": docids,
            "docs": docs,
            "doc_model": "school.teacher",
            "get_timetable_grid": self._get_timetable_grid,
        }
