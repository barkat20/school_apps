# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportTimetableInfo(models.AbstractModel):
    _name = "report.timetable.timetable"
    _description = "Timetable details"

    def _get_timetable(self, timetable_id):
        """Method to combain values for timetable"""
        timetable_detail = []
        self._cr.execute(
            """
                SELECT
                    t.start_time,
                    t.end_time,
                    s.name,
                    week_day,
                    st.employee_id,
                    hr.name as teacher,
                    t.is_ghost
                FROM
                    time_table_line t,
                    subject_subject s,
                    resource_resource r,
                    school_teacher st,
                    hr_employee hr
                WHERE
                    t.subject_id= s.id
                and
                    t.teacher_id=st.id
                and
                    st.employee_id= hr.id
                and
                    t.table_id = %s
                group by
                    start_time,end_time,
                    s.name,
                    week_day,
                    st.employee_id,
                    hr.name,
                    t.is_ghost
                order by start_time

            """,
            tuple([timetable_id.id]),
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
                    table_id=%s
                group by
                    start_time,end_time
                order by start_time
            """,
            tuple([timetable_id.id]),
        )
        time_data = self._cr.dictfetchall()
        for time_detail in time_data:
            # We will process all records for this time slot
            slot_records = [d for d in res if time_detail.get("start_time") == d.get("start_time") and time_detail.get("end_time") == d.get("end_time")]
            
            # Group by weekday
            by_day = {}
            for d in slot_records:
                by_day.setdefault(d["week_day"], []).append(d)
                
            for day, day_records in by_day.items():
                if any(d.get("name") == "Recess" for d in day_records):
                    time_detail[day] = "Recess"
                else:
                    # Check if it's a Sport Split (contains both ghost and real lines)
                    ghosts = [d for d in day_records if d.get("is_ghost")]
                    reals = [d for d in day_records if not d.get("is_ghost")]
                    
                    if ghosts and reals:
                        # Format as Sport / Subject
                        time_detail[day] = f"{ghosts[0].get('name')} / {reals[0].get('name')}\n({reals[0].get('teacher')})"
                    elif reals:
                        # Normal subject
                        time_detail[day] = f"{reals[0].get('name')}\n({reals[0].get('teacher')})"
                    elif ghosts:
                        time_detail[day] = f"{ghosts[0].get('name')}\n({ghosts[0].get('teacher')})"
                        
            timetable_detail.append(time_detail)
        return timetable_detail

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report data"""
        timetable_report = self.env["ir.actions.report"]._get_report_from_name(
            "timetable.timetable"
        )
        docs = self.env["time.table"].browse(docids)
        
        # Calculate dynamic active study days based on the conditions
        class_cond = self.env['timetable.class.condition'].search([], order='id desc', limit=1)
        active_days = []
        if class_cond:
            for day_name in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                if getattr(class_cond, f"day_{day_name}"):
                    active_days.append(day_name)
        else:
            active_days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
            
        return {
            "doc_ids": docids,
            "docs": docs,
            "data": data,
            "get_timetable": self._get_timetable,
            "active_days": active_days,
            "doc_model": timetable_report.model,
            "data": data,
            "get_timetable": self._get_timetable,
        }
