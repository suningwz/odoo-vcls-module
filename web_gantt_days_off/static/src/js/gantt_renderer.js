odoo.define('web_gantt_days_off.GanttRenderer', function (require) {
"use strict";

var GanttRenderer = require('web_gantt.GanttRenderer');


GanttRenderer.include({

    _render: function () {
        var self = this;
        var context = _.extend({}, this.state.context);
        return this._super().then(function(){
            if (context.gantt_colored_weekend) {
                self.$el.addClass('colored_weekends');
            }
        });
    },

});

});
