update ir_model_data
set module = 'vcls-suppliers',
name = 'suppliers_hours_product',
noupdate=true
where module = '__export__'
and name = 'product_template_712_5489ed70';