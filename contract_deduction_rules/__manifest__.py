# -*- coding: utf-8 -*-
{
    'name': 'Contract Deduction Rules',
    'summary': 'Contract Deduction Rules',
    'description': """
        This module add new salary rules to deduct like  social insurance and  social security.
    """
    ,
    'author': 'Amjad',
    'website': '',
    'depends': [
        'hr_payroll', 'hr_base_salary_structure'
    ],
    'data': [
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_inherit_view.xml',
        'views/menu_items_view.xml',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}
