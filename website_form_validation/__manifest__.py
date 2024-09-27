{
    "name": "Website Form  Validation",
    "summary": "Form Validation",
    'author': "Innona.do",
    'category': 'Website',
    'version': '17.0',
    "external_dependencies": {"python": ["phonenumbers"]},
    "license": "AGPL-3",
    "category": "Generic Modules",
    'data': [

        'views/auth_signup_login_templates.xml',
    ],

    "depends": ["website_sale", "phone_validation","account","auth_signup","website","portal"],
    "assets": {
            "web.assets_backend": [
                "website_form_validation/static/src/*.js",
            ],
            "web.assets_frontend": [
                "website_form_validation/static/src/css/passtrength.css",
            ]
        },
}
