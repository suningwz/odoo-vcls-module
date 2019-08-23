odoo.define('business_card_scanner.CardScanner', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');

var _t = core._t;
var QWeb = core.qweb;

var CardScanner = AbstractAction.extend({
    xmlDependencies: [
        '/vcls-business-card-scanner/static/src/xml/card_scanner.xml'
    ],
    template: 'card_scanner_template',
    events: {
        'click #camera--trigger': '_take_picture',
    },
    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.action = action;
        this.constraints = { video: { facingMode: "user" }, audio: false };
        this.track = null;
        this.set('title', _t('Scan Business card'));
    },
    start: function () {
        var self = this;
        var result = this._super.apply(this, arguments);
        const cameraView = this.$("#camera--view")[0];
        navigator.mediaDevices
        .getUserMedia(this.constraints)
        .then(function(stream) {
            self.track = stream.getTracks()[0];
            cameraView.srcObject = stream;
        })
        .catch(function(error) {
            console.error("Something is broken.", error);
        });

    },
    _take_picture: function () {
        const cameraView = this.$("#camera--view")[0];
        const cameraSensor = this.$("#camera--sensor")[0];
        const cameraOutput = this.$("#camera--output")[0];
        cameraOutput.classList.remove("taken");
        cameraSensor.width = cameraView.videoWidth;
        cameraSensor.height = cameraView.videoHeight;
        cameraSensor.getContext("2d").drawImage(cameraView, 0, 0);
        cameraOutput.src = cameraSensor.toDataURL("image/jpg");
        cameraOutput.classList.add("taken");
        this._rpc({
            model: 'res.partner',
            method: 'take_business_card_picture',
            args: [cameraOutput.src],
        }).then(function (result) {
        });
    },


});

core.action_registry.add('card.scanner', CardScanner);

return CardScanner;
});
