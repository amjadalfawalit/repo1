from odoo import fields, models, api, _

class remove_action(models.Model):
    _name = 'remove.action'
    _description = "Models Right"


    access_management_id = fields.Many2one('access.management', 'Access Management')
    model_id = fields.Many2one('ir.model', 'Model')
    view_data_ids = fields.Many2many('view.data', 'remove_action_view_data_rel_ah', 'remove_action_id', 'view_data_id', 'Views')
    server_action_ids = fields.Many2many('action.data' ,'remove_action_server_action_data_rel_ah', 'remove_action_id', 'server_action_id', 'Actions', domain="[('action_id.binding_model_id','=',model_id),('action_id.type','!=','ir.actions.report')]")
    report_action_ids = fields.Many2many('action.data' ,'remove_action_report_action_data_rel_ah', 'remove_action_id', 'report_action_id', 'Reports', domain="[('action_id.binding_model_id','=',model_id),('action_id.type','=','ir.actions.report')]")
    restrict_export = fields.Boolean('Restrict Export')
    readonly = fields.Boolean('Read-Only')

