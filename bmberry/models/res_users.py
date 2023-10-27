# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError



class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')
    only_members = fields.Boolean('Only Show Members')
    warehouse_ids = fields.Many2many('stock.warehouse','warehouse_security_stock_warehouse_users','user_id','warehouse_id', string='Active Locations')


