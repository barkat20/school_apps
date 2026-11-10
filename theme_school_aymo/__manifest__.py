{
    'name': 'Aymo ERP School Theme',
    'summary': 'Smooth and attractive theme using Aymo ERP colors for School Apps',
    'version': '18.0.1.0',
    'category': 'Themes',
    'description': """
        Aymo ERP School Theme
        =====================
        This theme applies the Aymo ERP color palette and modern UI styling to the Odoo backend.
        It features smooth rounded corners, soft gradients, and the official Aymo dark teal and cyan colors.
    """,
    'author': 'Your Company',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web._assets_primary_variables': [
            'theme_school_aymo/static/src/scss/primary_variables.scss',
        ],
        'web.assets_backend': [
            'theme_school_aymo/static/src/scss/backend_styles.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
