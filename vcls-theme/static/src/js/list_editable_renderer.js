odoo.define('vcls-theme.ListRenderer', function (require) {
"use strict";

var ListRenderer = require('web.ListRenderer');


ListRenderer.include({

    init: function (parent, state, params) {
        var self = this;
        // In edit mode and when this list is a Many2Many,
        // permit 'Add Line' functionality, as user have read access to the related model
        // 'Add Line' here allow only to select record,
        // but not to create a new ones (unless user has create access to related model)
        params.addCreateLine = params.addCreateLine || (params.isMany2Many && parent.mode === 'edit');
        // if user can select lines (add lines) so he can deselect (delete) them
        params.addTrashIcon = params.addTrashIcon || params.addCreateLine;
        return this._super.apply(this, arguments);
    },

});

});