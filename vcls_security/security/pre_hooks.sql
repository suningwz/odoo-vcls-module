update ir_model_data
set noupdate=false
where model='ir.rule'
and name='project_public_members_rule'
or name='task_visibility_rule'
and module='project';