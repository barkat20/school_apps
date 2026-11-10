# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class SchoolClassGroup(models.Model):
    _name = "school.class.group"
    _description = "School Class Group"

    name = fields.Char(string="Group Name", required=True)
    standard_id = fields.Many2one("school.standard", string="Class", required=True, ondelete='cascade')

class SchoolStandard(models.Model):
    _inherit = "school.standard"

    group_ids = fields.One2many("school.class.group", "standard_id", string="Groups")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # We attempt to dynamically find a representative name for this class depending on how the base school module manages standard records.
            class_name = ""
            if hasattr(record, 'name') and record.name:
                class_name = record.name
            elif hasattr(record, 'standard_id') and record.standard_id and getattr(record.standard_id, 'name', None):
                class_name = record.standard_id.name
            else:
                class_name = "Class"
                
            self.env['school.class.group'].create([
                {'name': f"{class_name} g1", 'standard_id': record.id},
                {'name': f"{class_name} g2", 'standard_id': record.id}
            ])
        return records

    def action_generate_groups(self):
        """Method to manually auto-generate class groups if they don't exist yet via a button."""
        for record in self:
            if not record.group_ids:
                class_name = ""
                if hasattr(record, 'name') and record.name:
                    class_name = record.name
                elif hasattr(record, 'standard_id') and record.standard_id and getattr(record.standard_id, 'name', None):
                    class_name = record.standard_id.name
                else:
                    class_name = "Class"
                    
                self.env['school.class.group'].create([
                    {'name': f"{class_name} g1", 'standard_id': record.id},
                    {'name': f"{class_name} g2", 'standard_id': record.id}
                ])
