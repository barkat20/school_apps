from odoo import models, fields

class TimetableGenerationResult(models.TransientModel):
    _name = "timetable.generation.result"
    _description = "Timetable Generation Result"

    message = fields.Html("Result Logs", readonly=True)
