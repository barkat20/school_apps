# See LICENSE file for full copyright and licensing details.

{
    "name": "Timetable Creator",
    "version": "18.0.1.0.0",
    "author": "Antigravity",
    "category": "School Management",
    "summary": "Constraint-based Timetable Generator Tool",
    "depends": ["school", "timetable"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_teacher_timetable_standard.xml",
        "report/report_class_timetable_men.xml",
        "wizard/timetable_generate_wizard_views.xml",
        "wizard/timetable_generation_progress_views.xml",
        "wizard/timetable_generation_result_views.xml",
        "wizard/timetable_force_assign_wizard_views.xml",
        "views/timetable_generation_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'timetable_creator/static/src/js/timetable_matrix.js',
            'timetable_creator/static/src/js/progress_poller.js',
        ],
    },
    "installable": True,
    "application": True,
}
