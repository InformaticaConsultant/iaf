{
    'name' : 'Aventura Financiera Theme',
    'description' : '''
        Aventura Financiera website theme
    ''',
    'version' : '17.0',
    'license' : 'LGPL-3',
    'depends' : ['website'],
    'data' : ['views/header.xml',
            'views/home.xml'],
    'assets':{
            'web.assets_frontend': [
                'aventura_financiera/static/css/styles.css',
                'aventura_financiera/static/js/init.js'
                ],
          },
    'installable' : True,
    'auto_install' : False,
}