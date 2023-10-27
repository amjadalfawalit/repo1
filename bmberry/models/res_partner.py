import logging
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)
import uuid 
from odoo.exceptions import AccessError,ValidationError


class Choices(models.Model):
    _name = "member.choices"
    
    name = fields.Char("Title")
    color = fields.Integer()


class Partner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [('member', 'unique(member_code)','Member Code Must Be uniuqe')]
    partner_map_address = fields.Char('Partner Map Address')
    partner_latitude = fields.Float(string='Partner Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Partner Geo Longitude', digits=(16, 5))
    active_member = fields.Boolean(string='Active Member')
    product_count = fields.Integer(compute='compute_count')
    current_location_ids = fields.One2many('stock.location', 'current_partner_id', string='Current Location')
    sale_percentage = fields.Float(string="Sales Profit Percentage For Member" ,readonly=lambda self: not self.user.has_group('bmberry.group_members_admin'))
    member_code = fields.Char("member code",index=True,size=6,help='Unique 6-letter member code')
    choices = fields.Many2many('member.choices')
    years_in_business = fields.Integer('Year in Business')

    @api.constrains('member_code')
    def _check_member_code(self):
        for member in self:
            if member.member_code and not member.member_code.isalpha() or len(member.member_code) != 6:
                raise ValidationError("Member code should contain only 6 letters.")

            if member.member_code and not member.member_code.isupper() or len(member.member_code) != 6:
                raise ValidationError("Member code should uppercase only 6 letters.")

    doc_count = fields.Char(compute='_compute_doc_count', string='doc_count')
    
    def _compute_doc_count(self):
        for record in self:
            record.doc_count = self.env['sign.template'].search_count([('partner_id', '=', record.id)])
        pass


    def get_docs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Signed Docs',
            'view_mode': 'kanban,tree',
            'res_model': 'sign.template',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }



    @api.onchange('member_code')
    def _onchange_member_code(self):
        if self._origin.member_code not in [False,'',"",None]:
            raise ValidationError("You Cant't Change Member Code")
        pass


    def compute_count(self):
        for record in self:
            record.product_count = self.env['product.template'].search_count([('member_id', '=', record.id)])

    def get_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'view_mode': 'tree,pivot',
            'res_model': 'product.template',
            'domain': [('member_id', '=', self.id)],
            'context': "{'create': False}"
        }



    def write(self, values):
        if 'sale_percentage' in values and not self.env.user.has_group('bmberry.group_members_admin'):
            raise AccessError("You don't have permission to update the 'Sales Profit Percentage for Member' field.")
        return super(Partner, self).write(values)