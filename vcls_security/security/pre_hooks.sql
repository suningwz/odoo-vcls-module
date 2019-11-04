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
    limit 1
);