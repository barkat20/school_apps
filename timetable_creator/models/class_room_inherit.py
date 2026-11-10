# See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ClassRoom(models.Model):
    _inherit = 'class.room'

    room_type_id = fields.Many2one('class.room.type', string='Room Type', help="Specifies if this room is a specialized facility (e.g. Lab, Gym).")
