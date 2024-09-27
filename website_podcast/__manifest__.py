# -*- coding: utf-8 -*-
{
    'name': "Website podcast",
    'summary': """This module creates a podcast section for the website.""",
    'description': """
        This module creates a podcast section for the website.
    """,
    "version":"17.0",
    'author': 'Raul Ovalle, raulovallet@gmail.com',
    'website': 'https://innova.do',
    'license': 'Other proprietary',
    'depends': [
        # Esto esta comentado porque si se actualiza borraria las cosas que estan hechas directamente en las vistas
        # 'base',
        'website',
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/website_podcast_views.xml',
        'views/website_podcast_templates.xml',
        'views/res_partner_views.xml',
    ],
    "assets": {
            "web.assets_frontend": [
                "website_podcast/static/src/js/podcast.js",
                "website_podcast/static/src/css/styles.css",
                "website_podcast/static/src/xml/website_podcast_searc_template.xml",
            ]
        },
    'installable': True,
    'auto_install': False
}
