# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    wage_type = fields.Selection([('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage'), ('daily', 'Daily Wage')], default='monthly',
                                 required=True)

    @api.model
    def create(self, vals):
        res = super(HrPayrollStructureType, self).create(vals)
        actual_work_hours_type = self.env.ref('hr_base_salary_structure.hr_rule_input_actual_work_hours',
                                              raise_if_not_found=False)
        if vals.get('wage_type', False):
            if vals.get('wage_type') == 'hourly':
                for structure in res.struct_ids:
                    if actual_work_hours_type and structure.id not in actual_work_hours_type.struct_ids.ids:
                        actual_work_hours_type.struct_ids += structure
                    basic_rules = structure.rule_ids.filtered(lambda x: x.code == 'BASIC')
                    for r in basic_rules:
                        r.write({
                            'amount_python_compute': 'result = (inputs.ACTWRKHINPT.amount * contract.hourly_wage) if inputs.ACTWRKHINPT else 0.0'
                        })
            elif vals.get('wage_type') == 'daily':
                for structure in res.struct_ids:
                    if actual_work_hours_type and structure.id in actual_work_hours_type.struct_ids.ids:
                        actual_work_hours_type.struct_ids -= structure
                    basic_rules = structure.rule_ids.filtered(lambda x: x.code == 'BASIC')
                    for r in basic_rules:
                        r.write({
                            'amount_python_compute': 'result = (worked_days.WORK100.number_of_days * contract.daily_wage) if worked_days.WORK100 else 0.0'
                        })
            else:
                for structure in res.struct_ids:
                    if actual_work_hours_type and structure.id in actual_work_hours_type.struct_ids.ids:
                        actual_work_hours_type.struct_ids -= structure
                    basic_rules = structure.rule_ids.filtered(lambda x: x.code == 'BASIC')
                    for r in basic_rules:
                        r.write({
                            'amount_python_compute': 'result = payslip.paid_amount'
                        })
        return res

    def write(self, vals):
        res = super(HrPayrollStructureType, self).write(vals)
        actual_work_hours_type = self.env.ref('hr_base_salary_structure.hr_rule_input_actual_work_hours',
                                              raise_if_not_found=False)
        if vals.get('wage_type', False):
            if vals.get('wage_type') == 'hourly':
                for type in self:
                    for structure in type.struct_ids:
                        if actual_work_hours_type and structure.id not in actual_work_hours_type.struct_ids.ids:
                            actual_work_hours_type.struct_ids += structure
                        basic_rules = structure.rule_ids.filtered(lambda x: x.code == 'BASIC')
                        for r in basic_rules:
                            r.write({
                                'amount_python_compute': 'result = (inputs.ACTWRKHINPT.amount * contract.hourly_wage) if inputs.ACTWRKHINPT else 0.0'
                            })
            elif vals.get('wage_type') == 'daily':
                for type in self:
                    for structure in type.struct_ids:
                        if actual_work_hours_type and structure.id in actual_work_hours_type.struct_ids.ids:
                            actual_work_hours_type.struct_ids -= structure
                        basic_rules = structure.rule_ids.filtered(lambda x: x.code == 'BASIC')
                        for r in basic_rules:
                            r.write({
                                'amount_python_compute': 'result = (worked_days.WORK100.number_of_days * contract.daily_wage) if worked_days.WORK100 else 0.0'
                            })
            else:
                for type in self:
                    for structure in type.struct_ids:
                        if actual_work_hours_type and structure.id in actual_work_hours_type.struct_ids.ids:
                            actual_work_hours_type.struct_ids -= structure
                        basic_rules = structure.rule_ids.filtered(lambda x: x.code == 'BASIC')
                        for r in basic_rules:
                            r.write({
                                'amount_python_compute': 'result = payslip.paid_amount'
                            })
        return res


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    @api.model
    def create(self, vals):
        res = super(HrPayrollStructure, self).create(vals)
        actual_work_hours_type = self.env.ref('hr_base_salary_structure.hr_rule_input_actual_work_hours',
                                              raise_if_not_found=False)
        if vals.get('type_id', False):
            if res.type_id.wage_type == 'hourly':
                if actual_work_hours_type and res.id not in actual_work_hours_type.struct_ids.ids:
                    actual_work_hours_type.struct_ids += res
                basic_rules = res.rule_ids.filtered(lambda x: x.code == 'BASIC')
                for r in basic_rules:
                    r.write({
                        'amount_python_compute': 'result = (inputs.ACTWRKHINPT.amount * contract.hourly_wage) if inputs.ACTWRKHINPT else 0.0'
                    })
            elif res.type_id.wage_type == 'daily':
                basic_rules = res.rule_ids.filtered(lambda x: x.code == 'BASIC')
                for r in basic_rules:
                    r.write({
                        'amount_python_compute': 'result = (worked_days.WORK100.number_of_days * contract.daily_wage) if worked_days.WORK100 else 0.0'
                    })
        return res

    def write(self, vals):
        res = super(HrPayrollStructure, self).write(vals)
        actual_work_hours_type = self.env.ref('hr_base_salary_structure.hr_rule_input_actual_work_hours',
                                              raise_if_not_found=False)
        if vals.get('type_id', False) and not vals.get('amount_python_compute', False):
            for rec in self:
                if rec.type_id.wage_type == 'hourly':
                    if actual_work_hours_type and rec.id not in actual_work_hours_type.struct_ids.ids:
                        actual_work_hours_type.struct_ids += rec
                    basic_rules = rec.rule_ids.filtered(lambda x: x.code == 'BASIC')
                    for r in basic_rules:
                        r.write({
                            'amount_python_compute': 'result = (inputs.ACTWRKHINPT.amount * contract.hourly_wage) if inputs.ACTWRKHINPT else 0.0'
                        })
                elif rec.type_id.wage_type == 'daily':
                    if actual_work_hours_type and rec.id in actual_work_hours_type.struct_ids.ids:
                        actual_work_hours_type.struct_ids -= rec
                    basic_rules = rec.rule_ids.filtered(lambda x: x.code == 'BASIC')
                    for r in basic_rules:
                        r.write({
                            'amount_python_compute': 'result = (worked_days.WORK100.number_of_days * contract.daily_wage) if worked_days.WORK100 else 0.0'
                        })
                else:
                    if actual_work_hours_type and rec.id in actual_work_hours_type.struct_ids.ids:
                        actual_work_hours_type.struct_ids -= rec
                    basic_rules = rec.rule_ids.filtered(lambda x: x.code == 'BASIC')
                    for r in basic_rules:
                        r.write({
                            'amount_python_compute': 'result = payslip.paid_amount'
                        })
        return res