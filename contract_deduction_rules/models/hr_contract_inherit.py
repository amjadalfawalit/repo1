# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    social_security_type = fields.Selection(selection=[('amount', 'Amount'), ('percentage', 'Percentage')],
                                            string='Social Security Type', default='amount',
                                            track_visibility='onchange')

    social_security = fields.Float(string='Social Security')
    social_security_percentage = fields.Float(string='Social Security Percentage')
    social_security_amount = fields.Float(string='Social Security Amount', compute='_compute_social_security_amount')

    social_insurance_type = fields.Selection(selection=[('amount', 'Amount'), ('percentage', 'Percentage')],
                                             string='Social Insurance Type', default='amount',
                                             track_visibility='onchange')
    social_insurance = fields.Float(string='Social Insurance')
    social_insurance_percentage = fields.Float(string='Social Insurance Percentage')
    social_insurance_amount = fields.Float(string='Social Insurance Amount', compute='_compute_social_insurance_amount')

    @api.onchange('wage', 'social_insurance_type', 'social_insurance', 'social_insurance_percentage')
    def _compute_social_insurance_amount(self):
        for contract in self:
            contract.social_insurance_amount = 0
            if contract.social_insurance_type == 'percentage':
                contract.social_insurance_amount = (contract.wage * contract.social_insurance_percentage) / 100

            elif contract.social_insurance_type == 'amount':
                contract.social_insurance_amount = contract.social_insurance

    @api.onchange('wage', 'social_security_type', 'social_security', 'social_security_percentage')
    def _compute_social_security_amount(self):
        for contract in self:
            contract.social_security_amount = 0
            if contract.social_security_type == 'percentage':
                contract.social_security_amount = (contract.wage * contract.social_security_percentage) / 100

            elif contract.social_security_type == 'amount':
                contract.social_security_amount = contract.social_security
           
    @api.constrains('social_security', 'social_security_percentage', 'social_insurance', 'social_insurance_percentage')
    def check_social_values(self):
        for contract in self:
            if contract.social_security_type == 'percentage':
                if contract.social_security_percentage <= 0:
                    raise ValidationError("Social security percentage should be greater than zero !")
                if contract.social_security_percentage >= 100:
                    raise ValidationError("Social security percentage should be less than 100% !")
            elif contract.social_security_type == 'amount':
                if contract.social_security <= 0:
                    raise ValidationError("Social security should be greater than zero !")

            if contract.social_insurance_type == 'percentage':
                if contract.social_insurance_percentage <= 0:
                    raise ValidationError("Social insurance percentage should be greater than zero !")
                if contract.social_insurance_percentage >= 100:
                    raise ValidationError("Social insurance percentage should be less than 100% !")
            elif contract.social_insurance_type == 'amount':
                if contract.social_insurance <= 0:
                    raise ValidationError("Social insurance should be greater than zero !")

    @api.onchange('social_security_type')
    def clear_social_security(self):
        for contract in self:
            contract.social_security = 0

    @api.onchange('social_insurance_type')
    def clear_social_insurance(self):
        for contract in self:
            contract.social_insurance = 0
    ssn = fields.Char('Social Security Number (SSN)',related='employee_id.ssn', tracking=True)



class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    ssn = fields.Char('Social Security Number (SSN)',tracking=True)
    driving_licenes = fields.Char('Driving Licenes Number')