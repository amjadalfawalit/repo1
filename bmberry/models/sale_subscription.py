from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'
    partner_id = fields.Many2one('res.partner',string='Members',domain=[('active_member','=',True)])

    

    def write(self,values):
        _logger.info('=============subsecription=============')
        _logger.info(values)
        stage_id = values.get('stage_id',False)
        recurring_invoice_line_ids = values.get('recurring_invoice_line_ids',False)
        old_stage_id = self.stage_id
        if old_stage_id.category == 'progress' and stage_id == False and recurring_invoice_line_ids != False:
            raise ValidationError("You Cant Edit Products In Running Stage Please Reset It To Draft")

        if stage_id != False:
            stage = self.env['sale.subscription.stage'].search([('id','=',stage_id)], limit=1)
            if stage.category == 'progress':
                _logger.info('----------------------------------------------------------------')
                for line in self.recurring_invoice_line_ids:
                    _logger.info(line.product_id.name)
                    product = line.product_id.product_tmpl_id
                    location_id = self.env['stock.location'].sudo().search([('id','=',product.stock_location_id.id)],limit=1)
                    if location_id.current_partner_id.id != False:
                        raise ValidationError("Location %s Already Active Rented By Member: %s" % (product.name,location_id.current_partner_id.name))


                    if location_id != False:
                        location_id.sudo().write({'current_partner_id':self.partner_id.id})

            elif stage.category != 'progress' and old_stage_id.category == 'progress':
                for line in self.recurring_invoice_line_ids:
                    _logger.info(line.product_id.name)
                    product = line.product_id.product_tmpl_id
                    location_id = self.env['stock.location'].sudo().search([('id','=',product.stock_location_id.id)],limit=1)
                    _logger.info(location_id.name)

                    if location_id != False:
                        location_id.sudo().write({'current_partner_id':False})
           
        
        return super(SaleSubscription, self).write(values)
