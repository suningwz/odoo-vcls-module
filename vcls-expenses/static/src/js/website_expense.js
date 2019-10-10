odoo.define('vcls-suppliers.website_project_expenses', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');

    var _t = core._t;

    if (!$('.website_portal_project_expenses').length) {
        return $.Deferred().reject("DOM doesn't contain '.website_portal_project_expenses'");
    }
    function build_modal(response){
        if (response && response.html) {
            var $modal = $(response.html);
            $('.website_portal_project_expenses').append($modal)
            $modal.modal('show');
            $modal.on('hidden.bs.modal', function () {
                $modal.remove();
            });
        }
    }
    $('.expense_delete').on('click', function (ev) {
        ev.preventDefault();
        var $form = $(ev.currentTarget).closest('form');
        var expense_id = $(ev.currentTarget).closest('tr').attr('value');
        var project_id = $('#project_id').attr('value');
        if (confirm(_t("Do you really want to delete this expense line?"))){
            $form.submit();
        }
    });

    $('.expense_edit').on('click', function (ev) {
        ev.preventDefault();
        var expense_id = $(ev.currentTarget).closest('tr').attr('value');
        var project_id = $('#project_id').attr('value');
        ajax.jsonRpc("/my/project/expense_modal", 'call', {
            'project_id': project_id,
            'expense_id': expense_id,
        }).then(build_modal);
    });

    $('.add_expense').on('click', function (ev) {
        ev.preventDefault();
        var project_id = $('#project_id').attr('value');
        ajax.jsonRpc("/my/project/expense_modal", 'call', {
            'project_id': project_id,
        }).then(build_modal);
    });

});
