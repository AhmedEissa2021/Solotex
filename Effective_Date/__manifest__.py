# -*- coding: utf-8 -*-
{
    'name': 'effective date in Stock Transfer',
    "author": "SBS",
    'version': '14.0.1.1',
    'summary': " stock back date ",
    'description': """ . """,
    "license" : "OPL-1",
    'depends': ['stock','purchase','purchase_stock','stock_account'],
    'data': [
        'views/stock.xml',
        'views/stock_quantity.xml',
        ],
    'installable': True,
    'auto_install': False,
    'category': 'Warehouse',
}
