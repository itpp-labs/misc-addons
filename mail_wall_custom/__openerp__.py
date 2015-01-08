{
    'name' : 'Custom mail wall',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Custom',
    'website' : 'https://it-projects.info',
    'description': """

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['gamification',
                 'gamification_extra',
                 'hr',
                 'sale',
                 'sales_team',
                 'crm',
                 'calendar',
                 'project',
                 'mail_wall_widgets',
                 'sale_mediation_custom',
                 'access_custom',
             ],
    'data':[
        'views.xml',
        'data.xml',
        ],
    'installable': True,
}
