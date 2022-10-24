# -*- coding: utf-8 -*
{
    "name": "pos powered by bsas",
    "category": "Point of Sale",
    "author": "Hussein Magdy",
    "summary":
        """
        POS Reciept Application Extend of Point Of Sale Odoo\n
        Supported Enterprise and Community \n
        Retail Stores & Restaurant Stores Supported \n\
        """,
    "description":
        """
        POS Reciept Application Extend of Point Of Sale Odoo\n
        Supported Enterprise and Community \n
        Included 300+ features of POS \n
        Retail Stores & Restaurant Stores Supported \n\
        """,

    "sequence": 1,
    "depends": ['point_of_sale',],
    "assets": {'web.assets_backend': [
    ],
        'web.assets_qweb': [
            'bsas_pos_reciept/static/src/xml/Screens/Receipt/OrderReceipt.xml',
        ],

    },


    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
}
