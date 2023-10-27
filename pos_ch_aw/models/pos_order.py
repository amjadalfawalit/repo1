# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_fields = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        payment_fields.update({
            'ch_approval_code': ui_paymentline.get('ch_approval_code'),
            'ch_transaction_id': ui_paymentline.get('ch_transaction_id'),
            'ch_card_number': ui_paymentline.get('ch_card_number'),
            'ch_gateway_ref': ui_paymentline.get('ch_gateway_ref'),
        })

        return payment_fields
