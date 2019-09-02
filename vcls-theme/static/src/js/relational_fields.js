odoo.define('vcls-theme.relational_fields', function (require) {
"use strict";
var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var dom = require('web.dom');
var ListController = require('web.ListController');
var ListView = require('web.ListView');
var pyUtils = require('web.py_utils');
var SearchView = require('web.SearchView');
var view_registry = require('web.view_registry');

var _t = core._t;

var relationnal_fields = require('web.relational_fields');
var FieldX2Many = relationnal_fields.FieldX2Many;

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