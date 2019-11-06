/*
Set update to false in project_public_members_rule
*/
update ir_model_data
set noupdate=false
where model='ir.rule'
and name='project_public_members_rule'
or name='task_visibility_rule'
and module='project';

/*
Deactivate the rule sale_order_rule_expense_user
that is restricting group_user from seeing sales order
*/
update ir_rule
set active = false
where id = (
    select coalesce(res_id, -1)
    from ir_model_data
    where model='ir.rule'
    and name='sale_order_rule_expense_user'
    and module='sale_expense'
    limit 1
);

/*
set noupdate to false for the following multi company rules
*/
update ir_model_data
set noupdate=false
where model='ir.rule'
and (
((name='project_comp_rule' or name='task_comp_rule')
    and module='project')
or ((name='analytic_comp_rule' or name='analytic_line_comp_rule'
     or name='analytic_group_comp_rule' or name='analytic_tag_comp_rule')
    and module='analytic')
or ((name='sale_order_comp_rule' or name='sale_order_line_comp_rule')
    and module='sale')
or (name='sale_team_comp_rule' and module='sales_team')
or ((name='tax_comp_rule' or name='journal_comp_rule'
    or name='invoice_comp_rule' or name='account_invoice_line_comp_rule'
    or name='account_payment_term_comp_rule' or name='account_fiscal_position_comp_rule'
    or name='account_comp_rule' or name='account_move_comp_rule'
    or name='account_move_line_comp_rule')
    and module='account')
)
