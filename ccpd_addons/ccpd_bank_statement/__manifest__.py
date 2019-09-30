# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CCPD Bank Statement',
    'version': '11.0.1.1.0',
    'category': 'Accounting',
    'author': "CAM NETWORK",
    'website': 'https://camnetwork.org',
    'summary': 'Override Bank Statement',
    "license": "LGPL-3",
    'depends': [
        "account",
    ],
    'data': [
        'views/account_bank_statement.xml',
    ],
}
