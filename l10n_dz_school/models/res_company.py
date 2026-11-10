# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    # Example defaults for Algerian context
    def _default_country_id(self):
        return self.env.ref('base.dz')
