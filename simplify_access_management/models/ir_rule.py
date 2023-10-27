# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools,_
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import config
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

class ir_rule(models.Model):
    _inherit = 'ir.rule'


    @api.model
    @tools.conditional(
        'xml' not in config['dev_mode'],
        tools.ormcache('self.env.uid', 'self.env.su', 'model_name', 'mode',
                       'tuple(self._compute_domain_context_values())'),
    )
    def _compute_domain(self, model_name, mode="read"):
        res = super(ir_rule,self)._compute_domain(model_name, mode)



        read_value = True
        self._cr.execute("SELECT state FROM ir_module_module WHERE name='simplify_access_management'")
        data = self._cr.fetchone() or False
        if data and data[0] != 'installed':
            read_value = False
        model_list = ['mail.activity','res.users.log','res.users','mail.channel','mail.alias','bus.presence','res.lang']
        if self.env.user.id and read_value:
            if model_name not in model_list:
                a = "select access_management_id from access_management_users_rel_ah where user_id = " + str(self.env.user.id)
                self._cr.execute(a)
                a = self._cr.fetchall()
                if a:
                    a = "SELECT id FROM access_management WHERE active='t' AND id in " + str(tuple([i[0] for i in a]+[0])) + " and readonly = True"
                    self._cr.execute(a)
                    a = self._cr.fetchall()
                if bool(a):
                    if mode != 'read' and model_name not in ['mail.channel.partner']:
                        raise UserError(_('%s is a read-only user. So you can not make any changes in the system!') % self.env.user.name)




        value = self._cr.execute("""SELECT value from ir_config_parameter where key='uninstall_simplify_access_management' """)
        value = self._cr.fetchone()
        if not value:
            if model_name:
                self._cr.execute("SELECT id FROM ir_model WHERE model='" + model_name +"'")
                model_numeric_id = self._cr.fetchone()[0]
                if model_numeric_id and isinstance(model_numeric_id,int) and self.env.user:
                    try:
                        self._cr.execute("""
                                        SELECT dm.id
                                        FROM access_domain_ah as dm
                                        WHERE dm.model_id=%s AND dm.apply_domain AND dm.access_management_id 
                                        IN (SELECT am.id 
                                            FROM access_management as am 
                                            WHERE active='t' AND am.id 
                                            IN (SELECT amusr.access_management_id
                                                FROM access_management_users_rel_ah as amusr
                                                WHERE amusr.user_id=%s))
                                        """,[model_numeric_id, self.env.user.id])
                    except:
                        pass
                    access_domain_ah_ids = self.env['access.domain.ah'].browse(row[0] for row in self._cr.fetchall())
                    if access_domain_ah_ids:
                        domain_list = []
                        eval_context = self._eval_context()
                        # only domain records
                        for access in access_domain_ah_ids.sudo():
                            dom = safe_eval(access.domain, eval_context) if access.domain else []
                            dom = expression.normalize_domain(dom)
                            left_user = False
                            for dom_tuple in dom:
                                if isinstance(dom_tuple,tuple):
                                    left_value = dom_tuple[0]
                                    operator_value = dom_tuple[1]
                                    right_value = dom_tuple[2]
                                    left_value_split_list = left_value.split('.')
                                    model_string = model_name
                                    left_user = False
                                    for field in left_value_split_list:
                                        left_user = False
                                        model_obj = self.env[model_string]
                                        field_type = model_obj.fields_get()[field]['type']
                                        if field_type in ['many2one','many2many','one2many']:
                                            field_relation = model_obj.fields_get()[field]['relation']
                                            model_string = field_relation
                                            if model_string == 'res.users':
                                                left_user = True


                                if left_user:
                                    if operator_value in ['in','not in']:
                                        if isinstance(right_value,list) and 0 in right_value:
                                            zero_index = right_value.index(0)
                                            right_value[zero_index] = self.env.user.id
                            domain_list.append(dom)
                        return expression.OR(domain_list)

        return res
