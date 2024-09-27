# -*- coding: utf-8 -*-
{
    "name": "Zoom - Odoo Events Connector",
    "summary": "Integrates Zoom with Events Platform",
    "description": """App which integrate Zoom with odoo Events to arrange Zoom online events. 
    """,
    'author': "Syncoria Inc.",
    'website': "https://www.syncoria.com",
    'company': 'Syncoria Inc.',
    'maintainer': 'Syncoria Inc.',
    "category": "Extra Tools",
    "version": "17.0",
    "depends": ["base_event_online"],    
    "images": [
        'static/description/banner.png',
    ],
    "data": [
        'views/res_config_settings_views.xml',
        'views/inherit_res_user_ZOOM.xml',
        'views/inherit_event_event.xml'

    ],
    'support': "support@syncoria.com",
    'price': 100,
    'currency': 'USD',
    'license': 'OPL-1',
    'support': "support@syncoria.com",
    'installable': True,
    'application': False,
    'auto_install': False,
}
