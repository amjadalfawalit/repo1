# -*- coding: utf-8 -*-
{
    'name': 'HR Base Salary Structure',
    'category': 'Human Resources',
    'summary': 'HR Base Salary Structure',
    'description': """
        This module adds the HR base salary structure.
    """
    ,
    'author': 'OSG',
    'website': '',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'data/hr_salary_rule_data.xml',
        'views/hr_contract_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}