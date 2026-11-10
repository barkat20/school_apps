# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportTeacherTimetableStandard(models.AbstractModel):
    _name = "report.timetable_creator.report_teacher_timetable_standard"
    _description = "Teacher Timetable Standard Details"

    def _get_timetable(self, teacher_id, table_ids):
        """Method to combine values for teacher timetable across selected tables"""
        timetable_detail = []
        if not table_ids:
            return timetable_detail
            
        self._cr.execute(
            """
                SELECT
                    t.start_time,
                    t.end_time,
                    sub.name as subject_name,
                    t.week_day,
                    ss.name as standard_name
                FROM
                    time_table_line t
                INNER JOIN subject_subject sub ON t.subject_id = sub.id
                INNER JOIN time_table tt ON t.table_id = tt.id
                INNER JOIN school_standard ss ON tt.standard_id = ss.id
                WHERE
                    t.teacher_id = %s
                    AND t.table_id IN %s
                GROUP BY
                    t.start_time, t.end_time,
                    sub.name,
                    t.week_day,
                    ss.name
                ORDER BY t.start_time
            """,
            (teacher_id.id, tuple(table_ids.ids)),
        )
        res = self._cr.dictfetchall()
        
        self._cr.execute(
            """
                SELECT
                    start_time,
                    end_time
                FROM
                    time_table_line
                WHERE
                    teacher_id=%s AND table_id IN %s
                GROUP BY
                    start_time, end_time
                ORDER BY start_time
            """,
            (teacher_id.id, tuple(table_ids.ids)),
        )
        time_data = self._cr.dictfetchall()
        
        for time_detail in time_data:
            for data in res:
                if (time_detail.get("start_time") == data.get("start_time")) and (
                    time_detail.get("end_time") == data.get("end_time")
                ):
                    td = data.get("subject_name") + "\n(" + data.get("standard_name") + ")"
                    time_detail[data["week_day"]] = td
            timetable_detail.append(time_detail)
        return timetable_detail

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report data for selected tables"""
        docs = self.env["time.table"].browse(docids)
        
        # Get all unique teachers across all selected timetables
        teacher_ids = docs.mapped('timetable_ids.teacher_id')
        
        return {
            "doc_ids": docids,
            "docs": teacher_ids,       # We iterate over teachers in Qweb
            "table_docs": docs,        # Pass tables so _get_timetable can filter by them
            "doc_model": "school.teacher",
            "data": data,
            "get_timetable": self._get_timetable,
        }
