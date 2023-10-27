import datetime
import logging
from odoo import models, api, fields,exceptions, _
_logger = logging.getLogger(__name__)


class StockLocationLog(models.Model):
    _name = "stock.location.log"
 
    partner_id = fields.Many2one('res.partner',string='Member')
    location_id = fields.Many2one('stock.location',string='Location')
    start_date = fields.Date(string='Date',default=False)
    end_date = fields.Date(string='Date',default=False)
    # field_name = fields.Float(compute='_compute_field_name', string='field_name')
    
    # @api.depends('')
    # def _compute_field_name(self):
    #     pass




class Subsecribtion(models.Model):
    _name = "subsecribtion.log"
 
    partner_id = fields.Many2one('res.partner',string='Member')
    location_id = fields.Many2one('stock.location',string='Location')
    
    date = fields.Date(string='Date',default=datetime.date.today())