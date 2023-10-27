import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    location = fields.Selection([
        ('MIDTOWN', 'MIDTOWN'),
        ('TOCO HILL', 'TOCO HILL'),
        ('ROSWELL', 'ROSWELL'),
        ('GREENVILLE SC', 'GREENVILLE SC'),
    ], string='Location')

    space_size_requested = fields.Selection([
        ('Triple', 'Triple'),
        ('Double', 'Double'),
        ('Single', 'Single'),
        ('End Cap', 'End Cap'),
        ('Half End cap', 'Half End cap'),
        ('1.5', '1.5'),
    ], string='Space Size Requested')

    has_other_space = fields.Boolean(
        string='Do You Currently Have a Space Somewhere Else?')
    other_space_duration = fields.Char(
        string='How Long Have You Had Your Space?')
    about_product = fields.Text(
        string='Tell Us About You and Your Product of Interest to Sell at Westside Market')
    customer_gender = fields.Selection([
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Other', 'Other'),
    ], string='Who is Your Customer?')

    product_price_point = fields.Float(
        string='What is Your Product Price Point?')
    first_time_business_owner = fields.Boolean(
        string='Is This Your First Time Owning Your Own Business?')
    why_westside_market = fields.Text(
        string='Why Do You Want to be a Part of Westside Market?')
    tour_date = fields.Date(
        string='What is the Best Date for You to Take a Tour?')
    tour_time = fields.Float(
        string='What is the Best Time for You to Take a Tour?')
    has_website = fields.Boolean(string='Do You Have a Website?')
    website_link = fields.Char(string='Website Link')
    instagram = fields.Char(string='Instagram')
    facebook = fields.Char(string='Facebook')
    heard_about_us = fields.Selection([
        ('Drove by a location', 'Drove by a location'),
        ('A friend told me', 'A friend told me'),
        ('Instagram', 'Instagram'),
        ('Facebook', 'Facebook'),
        ('Billboard', 'Billboard'),
    ], string='How Did You Hear About Us?')
    photos = fields.Many2many(
        'ir.attachment', string='Upload Photos of Your Work')

    def action_set_won(self):
        self.partner_id.active_member = True
        return super(CrmLead, self).action_set_won()

    # def action_set_lost(self, **additional_values):
    #     res = super().action_set_lost(**additional_values)
    #     self.mapped('partner_id').write({'active_member': False})
    #     return res

    def write(self, values):
        stage_id = values.get('stage_id')
        if stage_id:
            stage = self.env['crm.stage'].sudo().browse(stage_id)
            if stage.is_won:
                sale_percentage = float(self.env['ir.config_parameter'].sudo(
                ).get_param('bmberry.sale_percentage', default=0))
                self.mapped('partner_id').write({'active_member': True,
                                                 'sale_percentage': sale_percentage})
            # else:
            #     self.mapped('partner_id').write({'active_member': False,
            #                                      'sale_percentage': 0})
        return super(CrmLead, self).write(values)
