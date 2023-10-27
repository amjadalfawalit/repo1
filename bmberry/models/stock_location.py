from collections import defaultdict, OrderedDict
import datetime
import logging
from odoo import models, api, fields, exceptions, _
_logger = logging.getLogger(__name__)


class AnalayticTag(models.Model):
    _inherit = 'account.analytic.tag'

    stock_location_id = fields.Many2one(
        'stock.location', string='Related Stock Location')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Related Warehouse')


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    current_partner_id = fields.Many2one(
        'res.partner', string='Sales Partner', copy=False)
    analytic_tag_id = fields.Many2one(
        'account.analytic.tag', string="Analaytic tag", copy=False)
    user_ids = fields.Many2many('res.users', 'warehouse_security_stock_warehouse_users', 'warehouse_id', 'user_id', string='Managers', domain=lambda self: [
                                ('groups_id', 'in', self.env.ref('stock.group_stock_user').ids)], store=True, copy=False)

    @api.model
    def create(self, vals):
        res = super(Warehouse, self).create(vals)
        _logger.info(res)
        partner = self.env['res.partner'].create({
            'name': res.name + ' - ' + "Sales Partner",
        })

        analytic_tag = self.env['account.analytic.tag'].create({
            'name': res.name,
            'warehouse_id': res.id
        })
        res.current_partner_id = partner.id
        res.analytic_tag_id = analytic_tag.id

        return res


class LocationTypes(models.Model):
    _name = "location.type"

    name = fields.Char("Type Name", required=True, copy=False)
    price = fields.Float('Rent Price', required=True, copy=False)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', copy=False)

    def write(self, vals):
        res = super(LocationTypes, self).write(vals)
        if vals.get('price', False):
            for rec in self:
                locations = self.env['stock.location'].search(
                    [('location_type_id', '=', rec.id)])
                for item in locations:
                    item.subscription_product_template_id.list_price = float(
                        vals.get('price', 0.0))
        return res


class StockLocation(models.Model):

    _inherit = "stock.location"
    
    location_type_id = fields.Many2one(
        'location.type', string='Location Type', copy=False)
    current_partner_id = fields.Many2one(
        'res.partner', string='Current Member', copy=False)
    subscription_product_template_id = fields.Many2one(
        'product.template', string='Current template Product', copy=False, default=False)
    subscription_product_product_id = fields.Many2one(
        'product.product', string='Current product Product', copy=False, default=False)
    analytic_tag_id = fields.Many2one(
        'account.analytic.tag', string="Analaytic tag", copy=False)
    area = fields.Float('Area', copy=False)


    def write(self, vals):
        res = super(StockLocation, self).write(vals)
        if vals.get('name', False):
            for rec in self:
                location_name = res.location_id.name
                if location_name == False:
                    location_name = ''
                else:
                    location_name = res.location_id.name + '/'
                rec.subscription_product_template_id.name = location_name+rec.name,
        if vals.get('locaiton_id', False):
            for rec in self:
                location_name = res.location_id.name
                if location_name == False:
                    location_name = ''
                else:
                    location_name = res.location_id.name + '/'
                rec.subscription_product_template_id.name = location_name+rec.name,
        return res



    @api.model
    def create(self, vals):
        res = super(StockLocation, self).create(vals)
        location_name = res.location_id.name
        if location_name == False:
            location_name = ''
        else:
            location_name = res.location_id.name + '/'
    
        product_template_id = self.env['product.template'].sudo().create({
            'name': location_name+res.name,
            'sale_ok': True,
            'purchase_ok': False,
            'detailed_type': 'service',
            'taxes_id': False,
            'recurring_invoice': True,
            'list_price': res.location_type_id.price,
            'stock_location_id': res.id,
            'subscription_template_id': res.company_id.subscription_template_id.id
        })
        analytic_tag = self.env['account.analytic.tag'].create({
            'name': res.name,
            'stock_location_id': res.id
        })
        res.analytic_tag_id = analytic_tag.id
        res.subscription_product_template_id = product_template_id.id
    
        return res

    @api.depends('warehouse_view_ids')
    def _compute_warehouse_id(self):
        warehouses = self.env['stock.warehouse'].search(
            [('view_location_id', 'parent_of', self.ids)])
        view_by_wh = OrderedDict((wh.view_location_id.id, wh.id)
                                 for wh in warehouses)
        self.warehouse_id = False
        for loc in self:
            path = set(int(loc_id)
                       for loc_id in loc.parent_path.split('/')[:-1])
            for view_location_id in view_by_wh:
                if view_location_id in path:
                    loc.warehouse_id = view_by_wh[view_location_id]
                    break

    @api.onchange('location_id')
    def _compute_onchange_warehouse_id(self):
        for loc in self:
            loc.warehouse_id = self.location_id.warehouse_id.id
