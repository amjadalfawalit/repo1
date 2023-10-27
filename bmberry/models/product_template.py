import logging
from odoo import models, api, fields
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    api_image_url = fields.Char(
        "image url", size=300, compute='_compute_image_url')
    member_id = fields.Many2one('res.partner', string='Related Member', domain=[
                                ('active_member', '=', True)])
    stock_location_id = fields.Many2one(
        'stock.location', string='Related Stock Location' ,copy=False)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Related Warehouse', trctrack_visibility='onchange')

    member_barcode = fields.Char('Member Barcode')

    # location_ids = fields.Many2many(
    #     comodel_name='stock.location',
    #     string='Locations with Quantity',
    #     compute='_compute_location_ids',
    #     store=True
    # )

    # @api.depends('stock_quant_ids.location_id','stock_quant_ids')
    # def _compute_location_ids(self):
    #     for product in self:
    #         locations = product.stock_quant_ids.mapped('location_id')
    #         product.location_ids = [(6, 0, locations.ids)]

    # sales_count_stored = fields.Float(compute='_compute_sales_count_stored', string='Sold', digits='Product Unit of Measure',store=True)
    #
    #
    # @api.depends('sales_count')
    # def _compute_sales_count_stored(self):
    #     for obj in self:
    #         obj.sales_count_stored = obj.sales_count

    @api.depends('name')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        for obj in self:
            obj.api_image_url = base_url + '/web/image?' + \
                'model=product.template&id=' + \
                str(obj.id) + '&field=image_1920'


class ProductProduct(models.Model):

    _inherit = 'product.product'

    api_image_url = fields.Char(
        "image url", size=300, compute='_compute_image_url')
    stock_location_id = fields.Many2one(
        'stock.location', string='Related Stock Location',copy=False)
    warehouse_id = fields.Many2one('stock.warehouse', string='Related Warehouse',
                                   compute="_compute_warehouse", store=True, trctrack_visibility='onchange')

    @api.depends('qty_available')
    def _compute_warehouse(self):
        _logger.info('==========compute===========')
        for record in self:
            _logger.info('==========compute===========')
            _logger.info(record.detailed_type)
            if record.qty_available > 0 and record.detailed_type not in ['service', 'consu']:
                quants = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', record.id), ('on_hand', '=', True)], limit=1, order='id desc')
                _logger.info('==========compute===========')
                record.warehouse_id = quants.location_id.warehouse_id.id
                record.product_tmpl_id.warehouse_id = quants.location_id.warehouse_id.id

            else:
                record.warehouse_id = False
                record.product_tmpl_id.warehouse_id = False

    @api.depends('name')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        for obj in self:
            obj.api_image_url = base_url + '/web/image?' + \
                'model=product.product&id=' + str(obj.id) + '&field=image_1920'
