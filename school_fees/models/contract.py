# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SchoolAcademicContract(models.Model):
    _name = "school.academic.contract"
    _description = "Academic Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Contract Reference", readonly=True, default=lambda self: 'New')
    student_id = fields.Many2one("student.student", "Student", required=True, tracking=True)
    family_id = fields.Many2one(related="student_id.family_id", store=True, string="Family")
    year_id = fields.Many2one("academic.year", "Academic Year", required=True)
    template_id = fields.Many2one("school.contract.template", "Contract Template", required=True)
    installment_plan_id = fields.Many2one("school.installment.plan", "Installment Plan", required=True)
    discount_policy_id = fields.Many2one("school.discount.policy", "Discount Policy")
    
    line_ids = fields.One2many("school.academic.contract.line", "contract_id", "Fee Lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', tracking=True)
    
    invoice_ids = fields.One2many("account.move", "school_contract_id", "Invoices")
    invoice_count = fields.Integer("Invoice Count", compute="_compute_invoice_count")

    total_amount = fields.Float("Total Amount", compute="_compute_total_amount", store=True)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for contract in self:
            contract.invoice_count = len(contract.invoice_ids)

    def action_generate_invoices(self):
        self.ensure_one()
        if self.state != 'active':
            return
        
        move_obj = self.env['account.move']
        
        for plan_line in self.installment_plan_id.line_ids:
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': self.family_id.billing_contact_id.id or self.family_id.id,
                'school_contract_id': self.id,
                'invoice_date': fields.Date.today(), # Basic logic for demo purposes
                'invoice_line_ids': [],
            }
            
            percentage = plan_line.percentage / 100.0
            
            for fee_line in self.line_ids:
                amount_to_invoice = fee_line.subtotal * percentage
                if amount_to_invoice > 0:
                    invoice_vals['invoice_line_ids'].append((0, 0, {
                        'product_id': fee_line.category_id.product_id.id,
                        'name': f"{fee_line.category_id.name} - {plan_line.name}",
                        'quantity': 1,
                        'price_unit': amount_to_invoice,
                    }))
                    
            if invoice_vals['invoice_line_ids']:
                move_obj.create(invoice_vals)

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for contract in self:
            contract.total_amount = sum(line.subtotal for line in contract.line_ids)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.installment_plan_id = self.template_id.installment_plan_id
            lines = [(5, 0, 0)]
            for template_line in self.template_id.line_ids:
                lines.append((0, 0, {
                    'category_id': template_line.category_id.id,
                    'amount': template_line.amount,
                    'subtotal': template_line.amount
                }))
            self.line_ids = lines

class SchoolAcademicContractLine(models.Model):
    _name = "school.academic.contract.line"
    _description = "Contract Fee Line"

    contract_id = fields.Many2one("school.academic.contract", "Contract", required=True, ondelete="cascade")
    category_id = fields.Many2one("school.fee.category", "Fee Category", required=True)
    amount = fields.Float("Amount", required=True)
    discount = fields.Float("Discount")
    subtotal = fields.Float("Subtotal", compute="_compute_subtotal", store=True)

    @api.depends('amount', 'discount')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.amount - line.discount
