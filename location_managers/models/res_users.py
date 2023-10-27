# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError



class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')

    location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Warehouse Operations restrict')

