from odoo.tools import is_html_empty
from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_docs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Signed Docs',
            'view_mode': 'kanban,tree',
            'res_model': 'sign.template',
            'domain': [('order_id', '=', self.id)],
            'context': "{'create': False}"
        }

    doc_count = fields.Char(compute='_compute_doc_count', string='doc_count')

    def _compute_doc_count(self):
        for record in self:
            record.doc_count = self.env['sign.template'].search_count(
                [('order_id', '=', record.id)])
        pass

    def generate_contract(self):
        missing_fields = []
        for record in self:
            fields_to_check = [
                ('Member Code', record.partner_id.member_code),
                ('Create Date', record.create_date),
                ('VAT', record.partner_id.vat),
                ('Space Names', ','.join(
                    [line.product_id.product_tmpl_id.stock_location_id.name or '' for line in record.order_line])),
                ('Company Name', record.company_id.name),
                ('Amount Total', record.amount_total),
                ('Years in Business', record.partner_id.years_in_business),
                ('City', record.partner_id.city),
                ('State Name', record.partner_id.state_id.name),
                ('Street', record.partner_id.street),
                ('Zip Code', record.partner_id.zip),
                ('Mobile', record.partner_id.mobile),
                ('Email', record.partner_id.email)
            ]

            for field_name, field_value in fields_to_check:
                if field_value is None or not field_value:
                    missing_fields.append(field_name)

            if missing_fields:
                missing_fields_str = ', '.join(missing_fields)
                raise ValidationError(
                    f"The following required fields are missing or empty: {missing_fields_str}")
            content, content_type = self.env.ref(
                'bmb_templates.contract_report_action')._render(self.id)
            attachment = self.env['ir.attachment'].create({
                'type': 'binary',
                'raw': content,
                'name': f"{record.name}_{record.partner_id.name}_Contract.pdf",
            })
            main = self.env['sign.template'].search(
                [('is_main_template', '=', True)], limit=1)
            template = self.env['sign.template'].create({
                'attachment_id': attachment.id,
                'sign_item_ids': [(6, 0, [])],
                'order_id': record.id,
                'partner_id': record.partner_id.id
            })
            if main:
                for sign_item in main.sign_item_ids:
                    new_sign_item = sign_item.copy({
                        'template_id': template.id,
                    })
        return

    def _prepare_subscription_data(self, template):
        """Prepare a dictionnary of values to create a subscription from a template."""
        self.ensure_one()
        date_today = fields.Date.context_today(self)
        recurring_invoice_day = date_today.day
        recurring_next_date = self.env['sale.subscription']._get_recurring_next_date(
            template.recurring_rule_type, template.recurring_interval,
            date_today, recurring_invoice_day
        )
        values = {
            'name': template.name,
            'template_id': template.id,
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'payment_term_id': self.payment_term_id.id,
            'date_start': fields.Date.context_today(self),
            'description': self.note if not is_html_empty(self.note) else template.description,
            'pricelist_id': self.pricelist_id.id,
            'company_id': self.company_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'recurring_next_date': recurring_next_date,
            'recurring_invoice_day': recurring_invoice_day,
            'payment_token_id': self.transaction_ids._get_last().token_id.id if template.payment_mode == 'success_payment' else False,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
        }

        return values

    def create_subscriptions(self):
        """
        Create subscriptions based on the products' subscription template.

        Create subscriptions based on the templates found on order lines' products. Note that only
        lines not already linked to a subscription are processed; one subscription is created per
        distinct subscription template found.

        :rtype: list(integer)
        :return: ids of newly create subscriptions
        """
        res = []
        for order in self:
            to_create = order._split_subscription_lines()
            # create a subscription for each template with all the necessary lines
            for template in to_create:
                values = order._prepare_subscription_data(template)
                values['recurring_invoice_line_ids'] = to_create[template]._prepare_subscription_line_data()
                subscription = self.env['sale.subscription'].sudo().create(
                    values)
                subscription.onchange_date_start()
                res.append(subscription.id)
                to_create[template].write({'subscription_id': subscription.id})
                subscription.message_post_with_view(
                    'mail.message_origin_link', values={'self': subscription, 'origin': order},
                    subtype_id=self.env.ref(
                        'mail.mt_note').id, author_id=self.env.user.partner_id.id
                )
                self.env['sale.subscription.log'].sudo().create({
                    'subscription_id': subscription.id,
                    'event_date': fields.Date.context_today(self),
                    'event_type': '0_creation',
                    'amount_signed': subscription.recurring_monthly,
                    'recurring_monthly': subscription.recurring_monthly,
                    'currency_id': subscription.currency_id.id,
                    'category': subscription.stage_category,
                    'user_id': order.user_id.id,
                    'team_id': order.team_id.id,
                })
                default_stage = self.env['sale.subscription.stage'].search(
                    [('category', '=', 'progress')], limit=1)
                if default_stage:
                    subscription.write({
                        'stage_id':  default_stage.id,
                    })
                else:
                    raise UserError("No stage with category progress")
        return res

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', True)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    credit_card = fields.Boolean('Credit Card Payment', defualt=True)
    shipping = fields.Boolean('Shipping', defualt=False)

    # @api.onchange('order_line')
    # def compute_partner_warehouse(self):
    #         warehouse = self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1,offset=1)
    #         for recod in self :
    #             recod.warehouse_id = warehouse.id
    #             recod.partner_id = recod.warehouse_id.current_partner_id.id
    #             recod.partner_invoice_id = recod.partner_id.id
    #             recod.partner_shipping_id = recod.partner_id.id
    #             recod.pricelist_id  = recod.partner_id.property_product_pricelist.id

    def create_invoice_custome(self):
        order = self
        line_obj = self.env['account.move.line']
        analytic_account_obj = self.env['account.analytic.account']
        account_obj = self.env['account.account']
        sale_percentage = float(self.env['ir.config_parameter'].sudo(
        ).get_param('bmberry.sale_percentage', default=0))
        create_method = line_obj.sudo().with_context(check_move_validity=False).create
        product_sales_account = account_obj.search(
            [('code', '=', '400000')], limit=1)
        journal_com_1 = self.env['account.journal'].sudo().search(
            [('name', '=', 'Miscellaneous Operations'), ('company_id', '=', self.env.company.id)], limit=1)
        payment_journal = self.env['account.journal'].sudo().search(
            [('code', '=', 'CSH1'), ('type', 'in', ['cash'])], limit=1)
        try:
            invoice = order._create_invoices()
            invoice.action_post()
            for line in invoice.invoice_line_ids:
                _logger.info('============')
                _logger.info(line.product_id.product_tmpl_id.member_id)
                if line.product_id.product_tmpl_id.member_id.id != False:
                    sale_percentage = line.product_id.product_tmpl_id.member_id.sale_percentage
                    if order.credit_card:
                        sale_percentage = sale_percentage + 4

                    price_subtotal = line.price_subtotal
                    profit = price_subtotal * (sale_percentage / 100)
                    line_ids = [
                        (0, 0, {
                            'partner_id': line.product_id.product_tmpl_id.member_id.id,
                            'account_id': product_sales_account.id,
                            'company_id': invoice.company_id.id,
                            'credit': 0,
                            'debit': price_subtotal - profit}),
                        (0, 0, {
                            'partner_id': line.product_id.product_tmpl_id.member_id.id,
                            'account_id': line.product_id.product_tmpl_id.member_id.property_account_payable_id.id,
                            'company_id': invoice.company_id.id,
                            'credit': price_subtotal - profit,
                            'debit': 0}),
                    ]

                    move = self.env["account.move"].sudo().create({
                        "journal_id": journal_com_1.id,
                        'ref': "order_ref: " + str(order.name)+" Member Sales Revenue "+str(invoice.name) + " product " + line.product_id.product_tmpl_id.name,
                        'company_id': invoice.company_id.id,
                        "line_ids": line_ids,
                    })
                    move.action_post()

            payment = self.env['account.payment.register'].sudo().with_context(
                active_model='account.move', active_ids=invoice.ids).create({'journal_id': payment_journal.id})._create_payments()
            payment.action_post()
        except Exception as e:
            _logger.info('Error in Sale > Invoice creation %s', e)
            pass


class ResCompany(models.Model):
    _inherit = 'res.company'

    payment_journal_id = fields.Many2one('account.journal')
    vbill_journal_id = fields.Many2one('account.journal')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    sale_percentage = fields.Float(
        string="Sales Profit Percentage From Member", readonly=False, store=True)
    payment_journal_id = fields.Many2one('account.journal', 'Payment Journal',
                                         related="company_id.payment_journal_id",
                                         readonly=False,
                                         domain="[('company_id', '=', company_id), "
                                         "('type', 'in', ('bank', 'cash'))]")
    vbill_journal_id = fields.Many2one('account.journal', 'VBill Journal',
                                       related="company_id.vbill_journal_id",
                                       readonly=False,
                                       domain="[('company_id', '=', company_id), "
                                       "('type', '=', 'purchase')]")

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'bmberry.sale_percentage', self.sale_percentage)
        super(ResConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['sale_percentage'] = float(self.env['ir.config_parameter'].sudo(
        ).get_param('bmberry.sale_percentage', default=0))
        return res
