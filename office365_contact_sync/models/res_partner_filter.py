# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class ResPartnerFilter(models.Model):
    _name = 'res.partner.filter'

    name = fields.Char(string="Filter Name", required=True)

    default_enabled = fields.Boolean(string="Enabled by default", default=False)

    domain_filter = fields.Char(string='Domain Filter', help="Domains at user level get access to the res.partner record 'user' that is filtering its connected partners. Global filters do not, but have better performance.")
    python_filter = fields.Text(string='Python Code', help="Filters at user level get access to the res.partner record 'user' that is filtering its connected partners. Global filters do not, but have better performance. Function needs to return recordset with the records that follow this rule")

    # Level at which the filter should be calculated
    filter_level = fields.Selection(string='Filter Level', selection=[
        ('global', 'Global Filter'),
        ('user', 'User Specific Filter')
    ], default='global', help="Filters at user level get access to the res.partner record 'user' that is filtering its connected partners. Global filters do not, but have better performance.", required=True)

    # Type of filter, python code will execute python code to filter, domain will use domain to filter
    filter_type = fields.Selection(string='Filter Type', selection=[
        ('python', 'Python Code Filter'),
        ('domain', 'Domain Filter')
    ], default='domain', required=True)

    active = fields.Boolean('Active', default=True)

    @api.multi
    def get_filtered_partners_for_user(self, user):
        """Returns recordset with res.partner objects for a specific user, following the rules provided by self"""

        partner_obj = self.env['res.partner']
        records = self.env['res.partner']

        for f in self:
            if f.filter_type == 'python':
                shared_local_dict = {'env': self.env}

                if f.filter_level == 'user':
                    shared_local_dict['user'] = user

                safe_eval(f.python_filter, shared_local_dict, mode="exec", nocopy=True)

                r = shared_local_dict['result']
            else:
                r = partner_obj.search(safe_eval(f.domain_filter, locals_dict={'user': user}, nocopy=True))

            records += r

        # Removes duplicates
        return partner_obj.browse(set(records.ids))

    @api.model
    def get_globally_followed_filters(self, partner):
        """Returns recordset with the global filters that are followed by the provided res.partner record"""
        global_filters = self.search([('filter_level', '=', 'global')])

        followed_rules = []

        for f in global_filters:
            if f.is_following_rules(partner):
                followed_rules.append(f.id)

        return self.browse(followed_rules)

    @api.multi
    def is_following_rules(self, partner, user=None):
        """Returns True if provided res.partner record follows filters in self"""
        partner_obj = self.env['res.partner']

        for f in self:
            if f.filter_type == 'python':
                shared_local_dict = {'env': self.env}

                if f.filter_level == 'user':
                    shared_local_dict['user'] = user

                safe_eval(f.python_filter, shared_local_dict, mode="exec", nocopy=True)
                if partner in shared_local_dict['result']:
                    return True
            else:
                domain = safe_eval(f.domain_filter, locals_dict={'user': user}, nocopy=True)
                domain.insert(0, ('id', '=', partner.id))

                if partner_obj.search(domain):
                    return True

        return False
