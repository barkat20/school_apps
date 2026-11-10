# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class TimetableProgressController(http.Controller):
    
    @http.route('/timetable/generation/progress/<int:progress_id>', type='json', auth='user')
    def get_progress(self, progress_id, **kwargs):
        progress_record = request.env['timetable.generation.progress'].sudo().browse(progress_id)
        if not progress_record.exists():
            return {'state': 'error', 'progress': 0, 'log_messages': 'Progress record not found.'}
            
        return {
            'state': progress_record.state,
            'progress': progress_record.progress,
            'log_messages': progress_record.log_messages or '',
            'stage_name': progress_record.stage_name or 'Generating...'
        }
