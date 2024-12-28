# -*- coding: utf-8 -*-
{
    'name': 'SK odoo Quick Product Sale Order',
    'version': '17.0',
    'category': 'Sales/Sales',
    'summary': 'Quick Create Product in Sale Order',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',

        'views/sale_order_view.xml',

        'wizard/wizard_quick_product_view.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
