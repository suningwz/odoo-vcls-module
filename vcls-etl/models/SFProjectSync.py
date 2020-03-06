from . import ETL_SF
from . import generalSync
from . import SFProjectSync_constants
from . import SFProjectSync_mapping

import pytz
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
from tzlocal import get_localzone
from datetime import date
from datetime import datetime
from datetime import timedelta
import time
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api


class SFProjectSync(models.Model):
    #_name = 'etl.salesforce.project'
    _inherit = 'etl.sync.salesforce'

    project_sfid = fields.Char()
    project_sfname = fields.Char()
    project_sfref = fields.Char()
    so_ids = fields.Many2many(
        'sale.order',
        readonly = True,
    )
    project_ids = fields.Many2many(
        'project.project',
        readonly = True,
    )
    migration_status = fields.Selection(
        [
            ('todo', 'ToDo'),
            ('so', 'Sale Order'),
            ('structure', 'Structure'),
            ('ts', 'Timesheets'),
            ('complete', 'Complete'),
        ],
        default = 'todo', 
    )

    ####################
    ## MIGRATION METHODS
    ####################
    @api.model
    def initiate(self):
        instance = self.getSFInstance()

        query = """
        SELECT Id, Name, KimbleOne__Reference__c, Activity__c  
        FROM KimbleOne__DeliveryGroup__c 
        WHERE Automated_Migration__c = TRUE
        """
        records = instance.getConnection().query_all(query)['records']
        for rec in records:
            existing = self.search([('project_sfid','=',rec['Id'])],limit=1)
            if not existing:
                self.create({
                    'project_sfid': rec['Id'],
                    'project_sfname': rec['Name'],
                    'project_sfref': rec['KimbleOne__Reference__c'],
                })

        migrations = self.search([])
        for project in migrations:
            _logger.info("PROJECT MIGRATION STATUS | {} | {} | {}".format(project.project_sfref,project.project_sfname,project.migration_status))

    @api.model
    def test(self):
        instance = self.getSFInstance()
        projects = self.search([('migration_status','=','todo')])
        _logger.info("Processing {} Projects".format(projects.mapped('project_sfref')))
        projects.build_quotations(instance)
    
    @api.multi
    def build_quotations(self,instance):
        if not instance:
            return False

        #We get all the source data required for the projects in self
        project_string = self.list_to_filter_string(self.mapped('project_sfid'))
        element_data = self._get_element_data(instance,project_string)
        project_data = self._get_project_data(instance,project_string)
        assignment_data = self._get_assignment_data(instance,project_string)

        proposal_string = self.list_to_filter_string(project_data,'KimbleOne__Proposal__c')
        proposal_data = self._get_proposal_data(instance,proposal_string)
        
        element_string = self.list_to_filter_string(element_data,'Id')
        milestone_data = self._get_milestone_data(instance,element_string)
        activity_data = self._get_activity_data(instance,element_string)
        annuity_data = self._get_annuity_data(instance,element_string)

        #Then we loop to process projects separately
        for project in self:
            my_project = list(filter(lambda p: p['Id']==project.project_sfid,project_data))[0]
            if not project.so_ids: #no sale order yet
                #core_team
                core_team = self.env['core.team'].create(project.prepare_core_team_data(my_project,assignment_data))
                quote_data = project.prepare_so_data(project_data,proposal_data,element_data)
                if quote_data:
                    parent_id = False
                    for quote in sorted(quote_data,key=lambda q: q['index']):
                        vals = quote['quote_vals']
                        vals.update({'core_team_id':core_team.id})
                        if not parent_id:
                            _logger.info("PARENT SO CREATION VALS:\n{}".format(vals))
                            so = self.env['sale.order'].create(vals)
                            parent_id = so
                        else:
                            vals.update({'parent_id':parent_id.id})
                            _logger.info("CHILD CREATION VALS:\n{}".format(vals))
                            so = self.env['sale.order'].create(vals)

                        project.write({'so_ids':[(4, so.id, 0)]})
                        so.name = "{} | {}".format(vals['internal_ref'],vals['name'])
                        #we prepare line content
                        services_data = project.prepare_services(quote['elements'],so)
                        rates_data = project.prepare_rates(quote['elements'],activity_data,assignment_data)

                        #create lines
                        if services_data:
                            #we create a section
                            section = self.env['sale.order.line'].create({
                                'order_id':so.id,
                                'display_type': 'line_section',
                                'name':'Services',
                                })
                            for service in services_data:
                                self.env['sale.order.line'].create(service)
                        
                        if rates_data:
                            #we create a section
                            section = self.env['sale.order.line'].create({
                                'order_id':so.id,
                                'display_type': 'line_section',
                                'name':'Hourly Rates',
                                })
                        for rate in rates_data:
                            self.env['sale.order.line'].create({
                                'order_id':so.id,
                                'product_id': rate['product_id'],
                                'product_uom_qty':0,
                                'price_unit':rate['price'] if rate['price']>0 else False,
                                'section_line_id':section.id,
                                })

    def prepare_services(self,elements,sale_order):
        ouput=[]
        services = list(filter(lambda a: a['prod_info']['type']=='service',elements))
        for line in services:
            o_product = self.sf_id_to_odoo_rec(line['KimbleOne__Product__c'],line['Activity__c']) 
            if o_product:
                vals = {
                    'order_id':sale_order.id,
                    'name':line['Name'],
                    'product_id':o_product.id,
                    'product_uom_qty':1,
                    'price_unit':line['Contracted_Budget__c'] or line['KimbleOne__InvoicingCurrencyContractRevenue__c'],
                    #if fixed price, this is the sum of invoiced milestones
                }
                output.append(vals)
            else:
                _logger.info("No Odoo Product found for {}".format(line))
        return output

    
    ###
    def prepare_rates(self,elements,activity_data,assignment_data):
        rates = []
        for element in elements:
            if not element['prod_info']:
                _logger.info("MISSING PROD INFO FOR {} {}".format(element['KimbleOne__Reference__c'],element['KimbleOne__Product__c']))
                mode = 'tm'
            else:
                mode = element['prod_info']['mode']
            if mode in ['tm','fixed_price']: #if this element has assignement
                activities = list(filter(lambda a: a['KimbleOne__DeliveryElement__c']==element['Id'],activity_data))
                if activities:
                    activity = activities[0]
                    assignments = list(filter(lambda a: a['KimbleOne__ResourcedActivity__c']==activity['Id'],assignment_data))
                    for assignment in assignments:
                        o_rate_product = self.sf_id_to_odoo_rec(assignment['KimbleOne__ActivityRole__c'])
                        if o_rate_product:
                            #we check if already found
                            existing = list(filter(lambda p: p['product_id']==o_rate_product.id,rates))
                            if existing:
                                if assignment['KimbleOne__InvoicingCurrencyRevenueRate__c'] > existing[0]['price']: #if we found a cheaper one, we need to update it
                                    index = rates.index(existing[0])
                                    rates[index]['price']= assignment['KimbleOne__InvoicingCurrencyRevenueRate__c']
                                else:
                                    pass
                            else:
                                #we add a rate
                                rates.append({'name':o_rate_product.name,'product_id':o_rate_product.id,'price':assignment['KimbleOne__InvoicingCurrencyRevenueRate__c']})

        return sorted(rates,key=lambda r: r['price'],reverse = True)
               


    def prepare_core_team_data(self,my_project,assignment_data=False):
        core_team = {'name':"Team {}".format(my_project['KimbleOne__Reference__c'])}
        consultants = []

        #we get the LC
        o_user = self.sf_id_to_odoo_rec(my_project['OwnerId'])
        if o_user:
            employee = self.env['hr.employee'].with_context(active_test=False).search([('user_id','=',o_user.id)],limit=1)
            if employee:
                core_team['lead_consultant'] = employee.id

        #we look all assignments to extract resource data
        if assignment_data:
            assignments = list(filter(lambda a: a['KimbleOne__DeliveryGroup__c']==my_project['Id'],assignment_data))
            resources = self.values_from_key(assignments,'KimbleOne__Resource__c')
            resources = list(set(resources)) #get unique values
            for res in resources:
                emp = self.sf_id_to_odoo_rec(res)
                if emp:
                    consultants.append(emp.id)

            core_team['consultant_ids'] = [(6, 0, consultants)]

        return core_team


    def prepare_so_data(self,project_data,proposal_data,element_data):
        """
        We use a list of dict quote_data=
        {
            index: index of the element trigerring the new quotation
            quote_vals: data to call the create
            elements: sf_id of the elements linked to this quote
        }
        """
        self.ensure_one()
        quote_data = []

        my_project = list(filter(lambda project: project['Id']==self.project_sfid,project_data))[0]
        my_proposal = list(filter(lambda proposal: proposal['Id']==my_project['KimbleOne__Proposal__c'],proposal_data))[0]
        
        #we get useful exisitng records
        o_opp = self.sf_id_to_odoo_rec(my_proposal['KimbleOne__Opportunity__c'])
        o_company = self.sf_id_to_odoo_rec(my_proposal['KimbleOne__BusinessUnit__c'])

        #get useful fields values
        o_tag = self.env['crm.lead.tag'].search([('name','=','Automated Migration')],limit=1)
        tag = o_tag.id if o_tag else False
        currency_code = my_project['KimbleOne__InvoicingCurrencyIsoCode__c'] or o_company.currency_id.name
        o_pricelist = self.env['product.pricelist'].search([('name','=',"Standard {}".format(currency_code))],limit=1)
        if not o_pricelist:
            _logger.error("Pricelist not found {}".format(my_project['KimbleOne__InvoicingCurrencyIsoCode__c']))
            return False
        o_business_line = self.sf_id_to_odoo_rec(my_project['Activity__c'])
        bl = o_business_line.id if o_business_line else False

        my_elements = list(filter(lambda element: element['KimbleOne__DeliveryGroup__c']==my_project['Id'],element_data))

        quotations = self.split_elements(my_elements)
        index = 0
        for item in quotations:
            quote_vals = {
                'company_id':o_company.id,
                'partner_id':o_opp.partner_id.id,
                'user_id': o_opp.partner_id.user_id.id,
                'opportunity_id':o_opp.id,
                'internal_ref':("{}.{}".format(my_project['KimbleOne__Reference__c'],index) if index>0 else my_project['KimbleOne__Reference__c']).upper(),
                'name': (my_project['Name'] + (' -FP' if item['mode']=='fixed_price' else ' -TM')) if index>0 else my_project['Name'],
                'invoicing_mode':item['mode'] if item['mode'] else False,
                'pricelist_id':o_pricelist.id,
                'scope_of_work': my_project['Scope_of_Work_Description__c'],
                'expected_start_date':my_proposal['KimbleOne__DeliveryStartDate__c'] or date.today(),
                'expected_end_date':my_project['KimbleOne__ExpectedEndDate__c'],
                'tag_ids':[(4, tag, 0)],
                'product_category_id':bl,
            }
            quote_data.append({'index':item['min_index'],'quote_vals':quote_vals, 'elements':item['elements']})  
            index += 1

        return quote_data

    ###
    def split_elements(self,element_data):
        """
        We use a list of dict output=
        {
            min_index: used to prioritize quotation creation
            elements: elements data linked to this quote
        }
        """
        tm_group = {'min_index':100,'elements':[],'mode':'tm'}
        fp_group = {'min_index':100,'elements':[],'mode':'fixed_price'}
        others = {'min_index':100,'elements':[]}

        for element in sorted(element_data,key=lambda q: q['KimbleOne__Reference__c']):

            prod_info = list(filter(lambda info: info['sf_id']==element['KimbleOne__Product__c'][:-3],SFProjectSync_constants.ELEMENTS_INFO))
            mode = prod_info[0]['mode'] if prod_info else False
            index = int(element['KimbleOne__Reference__c'][-2:])
            element.update({'index':index,'prod_info':prod_info[0] if prod_info else False}) #we add this info for future use in SO lines creations
            
            #proposal = element['KimbleOne__OriginatingProposal__c']
            
            if mode=='tm':
                tm_group['elements'].append(element)
                if index < tm_group['min_index']:
                    tm_group['min_index'] = index
            elif mode=='fixed_price':
                fp_group['elements'].append(element)
                if index < fp_group['min_index']:
                    fp_group['min_index'] = index
            else:
                others['elements'].append(element)
                if index < others['min_index']:
                    others['min_index'] = index

        #we merge the groups
        if len(tm_group['elements'])>0:
            tm_group['elements'] = sorted(tm_group['elements'] + others['elements'],key=lambda q: q['index'])
            tm_group['min_index'] = min(tm_group['min_index'],others['min_index'])
        elif len(fp_group['elements'])>0:
            fp_group['elements'] = sorted(fp_group['elements'] + others['elements'],key=lambda q: q['index'])
            fp_group['min_index'] = min(fp_group['min_index'],others['min_index'])
        
        output = []
        if len(tm_group['elements'])>0:
            output.append(tm_group)
        if len(fp_group['elements'])>0:
            output.append(fp_group)
        return sorted(output,key=lambda q: q['min_index'])

    ###    
    def _get_element_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ELEMENT_DATA
        query += "WHERE Automated_Migration__c = TRUE AND KimbleOne__DeliveryGroup__c IN " + filter_string + " ORDER BY KimbleOne__Reference__c ASC"
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Elements".format(len(records)))
        
        return records

    def _get_project_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_PROJECT_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Projects".format(len(records)))
        
        return records

    def _get_proposal_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_PROPOSAL_DATA
        query += "WHERE Id IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Proposals".format(len(records)))
        
        return records
    
    def _get_milestone_data(self,instance,filter_string = False):
        #we get only revenue milestones
        query = SFProjectSync_constants.SELECT_GET_MILESTONE_DATA
        query += "WHERE KimbleOne__DeliveryElement__c IN " + filter_string + " AND KimbleOne__MilestoneType__c='a3d3A0000004bNb'"
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Milestones".format(len(records)))
        
        return records
    
    def _get_assignment_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ASSIGNMENT_DATA
        query += "WHERE KimbleOne__DeliveryGroup__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Assignments".format(len(records)))
        
        return records
    
    def _get_activity_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ACTIVITY_DATA
        query += "WHERE KimbleOne__DeliveryElement__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Resourced Activities".format(len(records)))
        
        return records
    
    def _get_annuity_data(self,instance,filter_string = False):
        query = SFProjectSync_constants.SELECT_GET_ANNUITY_DATA
        query += "WHERE KimbleOne__DeliveryElement__c IN " + filter_string
        _logger.info(query)

        records = instance.getConnection().query_all(query)['records']
        _logger.info("Found {} Annuities".format(len(records)))
        
        return records


    ######
    @api.model
    def _dev(self):
        instance = self.getSFInstance()
        self._get_time_entries(instance)
    

    def _get_time_entries(self,instance=False):
        
        query = """ 
            SELECT 
                Id,
                KimbleOne__DeliveryElement__c,
                KimbleOne__Category1__c,
                KimbleOne__Category2__c,
                KimbleOne__Category3__c,
                KimbleOne__Category4__c,
                KimbleOne__Notes__c,

                KimbleOne__InvoiceItemStatus__c,
                
                KimbleOne__TimePeriod__c,
                KimbleOne__Resource__c,
                KimbleOne__InvoicingCurrencyEntryRevenue__c,
                KimbleOne__EntryUnits__c,
                KimbleOne__ActivityAssignment__c,
                VCLS_Status__c
            FROM KimbleOne__TimeEntry__c
            WHERE KimbleOne__DeliveryElement__c IN ('a1U0Y00000BexAu','a1U0Y00000BexB4')
            AND VCLS_Status__c IN ('Billable - Draft','Billable - ReadyForApproval','Billable - Approved')
            """
            
            
        records = instance.getConnection().query_all(query)['records']
        for rec in records:
            _logger.info("{}\n{}".format(query,rec))
            break
        _logger.info("FOUND TIME ENTRIES {}".format(len(records)))



    ####################
    ## MAPPING METHODS
    ####################
    @api.model
    def build_reference_data(self):
        instance = self.getSFInstance()
        self._build_invoice_item_status(instance)
        self._build_milestone_type(instance)
        self._build_time_periods(instance)

    @api.model
    def build_maps(self):
        instance = self.getSFInstance()
        self._build_company_map(instance)
        self._build_product_map(instance)
        self._build_rate_map(instance)
        self._build_user_map(instance)
        self._build_activity_map(instance)
        self._build_resources_map(instance)
        self._test_maps(instance)


    ####################
    ## TOOL METHODS
    ####################
    def values_from_key(self,dict_list, key):
        output = []
        for item in dict_list:
            output.append(item[key])
        return output

    def sf_id_to_odoo_rec(self,sf_id,search_value = False):
        if search_value:
            key = self.env['etl.sync.keys'].search([('externalId','=',sf_id),('search_value','=',search_value),('odooId','!=',False)],limit=1)
        else:
            key = self.env['etl.sync.keys'].search([('externalId','=',sf_id),('odooId','!=',False)],limit=1)
        if key:
            return self.env[key.odooModelName].browse(int(key.odooId))
        else:
            return False
    
    def list_to_filter_string(self,list_in,key=False):
        stack = []
        for item in list_in:
            if key:
                stack.append("\'{}\'".format(item[key])) 
            else:
                stack.append("\'{}\'".format(item))  
        result = "({})".format(",".join(stack))
        return result
    
        
        

    



