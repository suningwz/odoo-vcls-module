update mail_template
set subject = '${object.partner_id.name} / VCLS invoice${(object.date_invoice and object.timesheet_limit_date and (" / " + str(object.date_invoice) + " - " + str(object.timesheet_limit_date) )) or ""}${(object.number and (" / " + object.number)) or "n/a"}'
where id = (
    select coalesce(res_id, -1)
    from ir_model_data
    where model='mail.template'
    and name='email_template_edi_invoice'
    and module='account'
    limit 1
);