# See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ClassRoomType(models.Model):
    _name = 'class.room.type'
    _description = 'Classroom Type'

    name = fields.Char('Room Type Name', required=True, help="e.g. PC Lab, Gymnasium, Chemistry Lab")
    description = fields.Text('Description')
