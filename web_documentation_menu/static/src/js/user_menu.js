odoo.define('web_documentation_menu.UserMenu', function (require) {
"use strict";

var core = require('web.core');
var UserMenu = require('web.UserMenu');
var ajax = require('web.ajax');

var qweb = core.qweb;
var _t = core._t;

UserMenu.include({

    start: function() {
        var session = this.getSession();
        var $el = this.$el;
        return this._super.apply(this, arguments).then(function () {
            if (!session.is_system){
                $el.find('[data-menu="support"]').hide();
            }
        });
    },
    _onMenuDocumentation: function () {
        return ajax.jsonRpc('/get/user/documentation', 'call')
        .then(function (data) {
            if (data.documentation_url){
                window.open(data.documentation_url, '_blank');
            }
        })
    },


});

return UserMenu;

});
