# coding: utf-8

from odoo import models, fields


class PosPayment(models.Model):
    _inherit = "pos.payment"

    ch_approval_code = fields.Char("CH Approval Code", readonly=True)
    ch_transaction_id = fields.Char("CH TransactionId", readonly=True)
    ch_card_number = fields.Char("CH Card Number", readonly=True)
    ch_gateway_ref = fields.Char("CH Gateway Reference", readonly=True)
