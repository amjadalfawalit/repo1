# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    profit_account_id = fields.Many2one('account.account', 'Profit Account')
    subscription_template_id = fields.Many2one('sale.subscription.template', 'Default Subscription template')


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    profit_account_id = fields.Many2one('account.account', 'Profit Account', related='company_id.profit_account_id', readonly=False)
    subscription_template_id = fields.Many2one('sale.subscription.template', 'Default Subscription template',  related='company_id.subscription_template_id', readonly=False )
