odoo.define('pos_ch_aw.models', function(require) {

    var models = require('point_of_sale.models');
    var PaymentChAw = require('pos_ch_aw.payment');

    models.register_payment_method('ch_aw', PaymentChAw);
    models.load_fields('pos.payment.method', ['ch_aw_terminal_ip']);

    var _paylineproto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        export_as_JSON: function() {
            return _.extend(_paylineproto.export_as_JSON.apply(this, arguments), {
                ch_transaction_id: this.ch_transaction_id,
                ch_approval_code: this.ch_approval_code,
                ch_gateway_ref: this.ch_gateway_ref,
            });
        },


    });

});