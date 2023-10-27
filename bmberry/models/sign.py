# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class SignTemplate(models.Model):
    _inherit = 'sign.template'
    is_main_template = fields.Boolean('is main template')
    partner_id = fields.Many2one('res.partner', string='partner')
    order_id = fields.Many2one('sale.order', string='order')
