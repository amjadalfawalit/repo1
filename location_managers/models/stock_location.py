# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many('res.users', 'location_security_stock_location_users', 'location_id', 'user_id', string='Managers',
                                domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').ids)],
                                store=True)

