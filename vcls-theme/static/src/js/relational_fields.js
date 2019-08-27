odoo.define('vcls-theme.relational_fields', function (require) {
"use strict";
var FieldX2Many = require('web.FieldX2Many');

FieldX2Many.include({

    /**
     *
     * @override
     * @private
     * @returns {Deferred|undefined}
     */
     
    _render: function () {
        if (!this.view) {
            return this._super();
        }
        if (this.renderer) {
            this.currentColInvisibleFields = this._evalColumnInvisibleFields();
            this.renderer.updateState(this.value, {'columnInvisibleFields': this.currentColInvisibleFields});
            this.pager.updateState({ size: this.value.count });
            return $.when();
        }
        var arch = this.view.arch;
        var viewType;
        var rendererParams = {
            arch: arch,
        };

        if (arch.tag === 'tree') {
            viewType = 'list';
            this.currentColInvisibleFields = this._evalColumnInvisibleFields();
            _.extend(rendererParams, {
                editable: this.mode === 'edit' && arch.attrs.editable,
                addCreateLine: !this.isReadonly && ( this.activeActions.create || this.isMany2Many),
                addTrashIcon: !this.isReadonly && this.activeActions.delete,
                isMany2Many: this.isMany2Many,
                columnInvisibleFields: this.currentColInvisibleFields,
            });
        }

        if (arch.tag === 'kanban') {
            viewType = 'kanban';
            var record_options = {
                editable: false,
                deletable: false,
                read_only_mode: this.isReadonly,
            };
            _.extend(rendererParams, {
                record_options: record_options,
            });
        }

        _.extend(rendererParams, {
            viewType: viewType,
        });
        var Renderer = this._getRenderer();
        this.renderer = new Renderer(this, this.value, rendererParams);

        this.$el.addClass('o_field_x2many o_field_x2many_' + viewType);
        return this.renderer ? this.renderer.appendTo(this.$el) : this._super();
    },
     
     });

});