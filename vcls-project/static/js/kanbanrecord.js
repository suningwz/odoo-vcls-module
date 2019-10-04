odoo.define('vcls-project.update_kanban', function (require) {
'use strict';

var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    _openRecord: function () {
            var parent = this.$el.parent();
            if (parent !== 'undefined' && !(parent.hasClass('o_vcls_open_form'))) {
                 return this._super.apply(this, arguments);
            }
            if (this.$el.hasClass('o_currently_dragged')) {
            // this record is currently being dragged and dropped, so we do not
            // want to open it.
            return;
            }
            var editMode = this.$el.hasClass('oe_kanban_global_click_edit');
            this.trigger_up('open_record', {
                id: this.db_id,
                mode: editMode ? 'edit' : 'readonly',
            });
        },
});
});