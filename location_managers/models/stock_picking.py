# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _user_locations(self):
        locations = self.env.user.location_ids
        return [('id', 'in', locations.ids)] if locations else []

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})

    is_location_manager = fields.Boolean(compute='_check_location_manger')
    is_dest_location_manager = fields.Boolean(compute='_check_location_manger')

    @api.depends('location_id', 'location_dest_id', 'picking_type_code')
    def _check_location_manger(self):
        for record in self:
            is_location_manager = False
            is_dest_location_manager = False
            if record.picking_type_code != 'internal' or (self.env.user.id in record.location_id.user_ids.ids and record.picking_type_code == 'internal'):
                is_location_manager = True
            if self.env.user.id in record.location_dest_id.user_ids.ids:
                is_dest_location_manager = True
            record.is_location_manager = is_location_manager
            record.is_dest_location_manager = is_dest_location_manager

    @api.depends('state', 'is_locked', 'location_id', 'location_dest_id', 'picking_type_code')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned') or not picking.is_locked:
                picking.show_validate = False
            else:
                if (picking.picking_type_code != 'outgoing' and self.env.user.id in picking.location_dest_id.user_ids.ids) \
                    or (picking.picking_type_code == 'outgoing' and self.env.user.id in picking.location_id.user_ids.ids):
                    picking.show_validate = True
                else:
                    picking.show_validate = False

