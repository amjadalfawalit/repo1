odoo.define('pos_six.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosChAWChrome = (Chrome) =>
        class extends Chrome {
            get balanceButtonIsShown() {
                return this.env.pos.payment_methods.some(pm => pm.use_payment_terminal === 'ch_aw');
            }
        };

    Registries.Component.extend(Chrome, PosChAWChrome);

    return Chrome;
});
