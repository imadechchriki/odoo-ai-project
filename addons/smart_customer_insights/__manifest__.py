{
    'name': 'Smart Customer Insights',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Analyse intelligente des clients avec IA',
    'description': '''
        Module d'analyse client avec Intelligence Artificielle
        ========================================================
        * Analyse de sentiment automatique
        * Génération de résumés intelligents
        * Suggestions d'actions commerciales
        * Dashboard IA
    ''',
    'author': 'Votre Nom',
    'website': 'https://www.example.com',
    'depends': ['base', 'contacts', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/customer_insight_views.xml',
        'views/menu_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}