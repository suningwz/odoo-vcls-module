odoo.define('mail_customer_no_auto_subscribe.mail.composer.Chatter', function (require) {
"use strict";

var ChatterComposer = require('mail.composer.Chatter');

ChatterComposer.include({

    init: function (parent, model, suggestedPartners, options) {
        _.each(suggestedPartners, function (suggestedPartner) {
            suggestedPartner.checked = false;
        });
        this._super.apply(this, arguments);
    },

});

return ChatterComposer;

});
