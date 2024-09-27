# -*- coding: utf-8 -*-
{
    'name': "base_event_online",

    "summary": "Syncoria Odoo Events Integration Base",
    "description": """
    Odoo Events Integration Base
    """,
    'author': "Syncoria Inc.",
    'website': "https://www.syncoria.com",
    'company': 'Syncoria Inc.',
    'license': 'OPL-1',
    'support': "support@syncoria.com",
    'maintainer': 'Syncoria Inc.',
    "category": "Extra Tools",
    "version": "17.0",
    "depends": ["base","event","website","website_event","website_profile"],
    'data': [
        'views/inherit_event_event.xml',
        'views/inherit_event_registration.xml',
        #'views/inherit_event_website_template.xml', No es necesario migrarla
        'views/res_config_settings_views.xml',
        'views/inherit_res_users.xml',


    ],
  
}
