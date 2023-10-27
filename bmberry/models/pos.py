from odoo import fields, models, api, exceptions, _
from collections import defaultdict
from odoo.tools.safe_eval import safe_eval
from odoo.tests.common import Form
import logging
_logger = logging.getLogger(__name__)

class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    per_ded = fields.Float('Deduction Percentage')




class AccountMove(models.Model):
    _inherit = "account.move"
    pos_order_id = fields.Many2one('pos.order',readonly=True)


class PosOrder(models.Model):
    _inherit = "pos.order"
    
    related_journal_entry_ids =  fields.One2many('account.move','pos_order_id', readonly=True,string="Related JVs")

    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()
        self.create_commission_bill()
        return res

    def create_commission_bill(self):
        for order in self:
            _logger.info(order.name)
            per_ded = max(order.payment_ids.mapped('payment_method_id.per_ded'))

            _logger.info('==========pos==================')
            account_obj = self.env['account.account']
            sale_percentage = float(self.env['ir.config_parameter'].sudo().get_param('bmberry.sale_percentage', default=0))
            product_sales_account =  account_obj.search([('code','=','400000')],limit=1)
            journal_com_1 = self.env['account.journal'].sudo().search([('name','=','Miscellaneous Operations'),('company_id','=',self.env.company.id)], limit=1)
            for line in order.lines.filtered('product_id.member_id.sale_percentage'):
                if line.product_id.product_tmpl_id.member_id.id != False:
                    sale_percentage = line.product_id.product_tmpl_id.member_id.sale_percentage + per_ded

                    price_subtotal = line.price_subtotal
                    if price_subtotal < 0 :
                        price_subtotal = -1 * line.price_subtotal

                        profit = price_subtotal * (sale_percentage / 100)
                        line_ids =  [
                                (0, 0, {
                                'partner_id': line.product_id.product_tmpl_id.member_id.id,
                                'account_id': product_sales_account.id,
                                'company_id':  order.company_id.id,
                                'debit': 0,
                                'credit': price_subtotal - profit}),
                                (0, 0, {
                                    'partner_id': line.product_id.product_tmpl_id.member_id.id,
                                    'account_id': line.product_id.product_tmpl_id.member_id.property_account_payable_id.id,
                                    'company_id':  order.company_id.id,               
                                    'debit': price_subtotal - profit,
                                    'credit': 0}),
                             ]
                    else:
                        profit = price_subtotal * (sale_percentage / 100)
                        line_ids =  [
                                (0, 0, {
                                'partner_id': line.product_id.product_tmpl_id.member_id.id,
                                'account_id': product_sales_account.id,
                                'company_id':  order.company_id.id,
                                'credit': 0,
                                
                                'debit': price_subtotal - profit}),
                                (0, 0, {
                                    'partner_id': line.product_id.product_tmpl_id.member_id.id,
                                    'account_id': line.product_id.product_tmpl_id.member_id.property_account_payable_id.id,
                                    'company_id':  order.company_id.id,               
                                    'credit': price_subtotal - profit,
                                    'debit': 0}),
                             ]
        
        
                    move = self.env["account.move"].sudo().create({
                        "journal_id": journal_com_1.id,
                        'pos_order_id' : order.id,
                        'company_id' :  order.company_id.id,
                        "line_ids": line_ids,
                    })
                    move.action_post()
                    move.write({
                        'ref': "Pos Order : order ref: " + str(order.name)+" Member Sales Revenue " + " product "+ line.product_id.product_tmpl_id.name
                    })






