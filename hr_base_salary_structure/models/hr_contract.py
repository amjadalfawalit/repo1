# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_type = fields.Selection([('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage'), ('daily', 'Daily Wage')], related='structure_type_id.wage_type', store=1)
    daily_wage = fields.Monetary('Daily Wage', digits=(16, 2), default=0, tracking=True,
                                  help="Employee's daily gross wage.")

