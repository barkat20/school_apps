# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    school_contract_id = fields.Many2one("school.academic.contract", "Academic Contract", readonly=True)
