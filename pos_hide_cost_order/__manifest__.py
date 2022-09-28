# -*- coding: utf-8 -*
# TL Technology (thanhchatvn@gmail.com)
# OPL-1 license
# Not allow resale, editing source codes
# License: Base on Odoo Proprietary License v1.0
{
    "name": "POS Restrict On Click Product",
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

    "sequence": 0,
    "depends": ['point_of_sale'],
    "assets": {

        'web.assets_backend': [

        ],

        'web.assets_qweb': ['pos_hide_cost_order/static/src/xml/Popups/ProductInfoPopup.xml'],

    },


    "currency": "EUR",
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
}
