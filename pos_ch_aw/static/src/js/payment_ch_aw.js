var s = 1;
odoo.define('pos_ch_aw.payment', function(require) {
    "use strict";

    const {
        Gui
    } = require('point_of_sale.Gui');
    var core = require('web.core');
    var PaymentInterface = require('point_of_sale.PaymentInterface');

    var _t = core._t;

    //var onTimApiReady = function () {};
    //var onTimApiPublishLogRecord = function (record) {
    //    // Log only warning or errors
    //    if (record.matchesLevel(timapi.LogRecord.LogLevel.warning)) {
    //        timapi.log(String(record));
    //    }
    //};

    var PaymentChAw = PaymentInterface.extend({

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        init: function() {
            this.toResolve = false;
            console.log(arguments);
            console.log('4444444444');
            this._super.apply(this, arguments);
            //            this.enable_reversals();
            var terminal_ip = this.payment_method.ch_aw_terminal_ip;
        },

        /**
         * @override
         */
        send_payment_cancel: function(order, cid) {
            this._super.apply(this, arguments);
            this._socket.close(1000, 'send_payment_cancel');
            this.tranResolve(false);
            this.pos.get_order().selected_paymentline.set_payment_status('waitingCancel');
            return Promise.reject();
        },

        /**
         * @override
         */
        close: function() {
            this._socket.close(1000, 'close');
            this.tranResolve(false);
        },


        send_payment_request: function(cid) {
            this._super.apply(this, arguments);
            var self = this;
            console.log(cid);
            this.prom = new Promise((resolve) => {
                this.transactionResolve = resolve
                this.toResolve = true;
            });
            console.log(this.pos.get_order().selected_paymentline);
            var is_sent = this.prepare_payment_request();
            if (is_sent == true) {
                this.pos.get_order().selected_paymentline.set_payment_status('waitingCard');
            } else {
                this.tranResolve(false)
            }
            return this.prom;
        },


        prepare_payment_request: function() {
            var order = this.pos.get_order()
            var amount = order.selected_paymentline.get_amount();
            var body = "ChargeanywhereProcessTransaction://?version=1.0&tenderType=2&clerkNumber=clr&";
            body += "invoiceNumber=" + order.uid + "&";

            if (amount > 0) {
                body += "transactionType=1&";
            } else if (amount < 0) {
                body += "transactionType=3&";
            } else {
                Gui.showPopup('ErrorPopup', {
                    title: _t('Transaction was not processed correctly'),
                    body: "The amount shouldn't be zero!",
                });
                return false;
            }
            body += "&saleAmount=" + Math.abs(amount)
            this.send_data(body, order.selected_paymentline);
            console.log(body);
            return true;
        },

        tranResolve: function(r) {
            if (this.toResolve == true) {
                this.transactionResolve(r);
                this.toResolve = false;
            }
        },


        send_data: function(data, selected_paymentline) {
            var self = this;
            this._socket = new WebSocket(this.payment_method.ch_aw_terminal_ip);
            console.log(11111111111)
            var s = this._socket;
            s.onopen = function(event) {
                console.log('onopen');
                console.log(event);
                s.send(data);

            };
            s.onmessage = function(event) {
                console.log('onMessage');
                console.log(event);
                var data_map = new Object()
                var data = event.data.split("//?")[1].split("&");
                for (var i = 0; i < data.length; i++) {
                    var item = data[i].split("=");
                    data_map[item[0]] = item[1];

                }
                console.log(data_map);
                if (data_map.TransactionResult === "APPROVED" &&
                    data_map.responseCode === "000"
                ) {
                    if (parseFloat(data_map.authorizedAmount) > 0) {
                        selected_paymentline.set_amount(parseFloat(data_map.authorizedAmount));
                        selected_paymentline.ch_transaction_id = data_map.transactionId;
                        selected_paymentline.ch_approval_code = data_map.approvalCode;
                        selected_paymentline.ch_gateway_ref = data_map.gatewayReferenceNumber || "";
                        selected_paymentline.cardholder_name = data_map.nameOnCard || "";
                        selected_paymentline.card_type = data_map.cardType || "";;
                        self.tranResolve(true);
                    }

                }
                s.close(1000, "Work complete")

            };
            s.onclose = function(event) {
                console.log('onclose');
                console.log(event);
                self.tranResolve(false);
                if (!event.wasClean) {
                    Gui.showPopup('ErrorPopup', {
                        title: _t('Transaction was not processed correctly'),
                        body: "Kindly make sure that the payment machine is working and connected to the internet!",
                    });
                }


            };
            s.onerror = function(error) {
                console.log('onerror');
                console.log(error);

            };

            this.payment_method._socket = this._socket;

        },

    });

    return PaymentChAw;

});