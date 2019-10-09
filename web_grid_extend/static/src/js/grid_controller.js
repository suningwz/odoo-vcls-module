odoo.define('web_grid_extend.GridController', function (require) {
"use strict";

var core = require('web.core');
var dialogs = require('web.view_dialogs');
var utils = require('web.utils');
var GridController = require('web_grid.GridController');

var qweb = core.qweb;
var _t = core._t;

GridController.include({

    // this method is executed on lens click on grid view
    // here we will add the ability to show custom action on lens click
    _onClickCellInformation: function (e) {
        var self = this;
        var $target = $(e.target);
        var cell_path = $target.parent().attr('data-path').split('.');
        var row_path = cell_path.slice(0, -3).concat(['rows'], cell_path.slice(-2, -1));
        var state = this.model.get();
        var cell = utils.into(state, cell_path);
        var row = utils.into(state, row_path);

        var groupFields = state.groupBy.slice(_.isArray(state) ? 1 : 0);
        var label = _.map(groupFields, function (g) {
            return row.values[g][1] || _t('Undefined');
        }).join(': ');

        // pass group by, section and col fields as default in context
        var cols_path = cell_path.slice(0, -3).concat(['cols'], cell_path.slice(-1));
        var col = utils.into(state, cols_path);
        var column_value = col.values[state.colField][0] ? col.values[state.colField][0].split("/")[0] : false;
        var ctx = _.extend({}, this.context);

        var sectionField = _.find(this.renderer.fields ,function(res) {
            return self.model.sectionField === res.name;
        });
        if (this.model.sectionField && state.groupBy && state.groupBy[0] === this.model.sectionField) {
            var value = state[parseInt(cols_path[0])].__label;
            ctx['default_' + this.model.sectionField] = _.isArray(value) ? value[0] : value;
        }
        _.each(groupFields, function (field) {
            ctx['default_'+field] = row.values[field][0] || false;
        });

        ctx['default_'+state.colField] = column_value;

        this._rpc({
            model: this.modelName,
            method: 'show_grid_cell',
            args: [cell.domain, column_value, row.values],
            context: ctx,
        }).then(function(action){
            if (action){
                self.do_action(action, {
                    on_close: function(){
                        // update the view on popup close
                        var state = self.model.get();
                        self.model.reload()
                        .then(function () {
                            var state = self.model.get();
                            return self.renderer.updateState(state, {});
                        }).then(function () {
                            self._updateButtons(state);
                        });
                    }
                });
            }else{
                // if action is empty or not defined
                // make normal behaviour on grid view
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: label,
                    res_model: self.modelName,
                    views: [
                        [self.listViewID, 'list'],
                        [self.formViewID, 'form']
                    ],
                    domain: cell.domain,
                    context: ctx,
                });
            }
        });
    },

});

return GridController;

});
