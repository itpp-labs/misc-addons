{
    'name' : 'Last viewed records (OBSOLETE)',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Hidden',
    'website' : 'https://yelizariev.github.io',
    'description': """
*This is a frozen version. The module is moved to OCA's repo. Check out newest version here:*  https://github.com/OCA/web/tree/8.0/web_last_viewed_records

The idea is taken from SugarCRM's "Last viewed" feature.

This module doesn't affect on server performance, because it uses browser's localStorage to save history. But dissadvantage is that history is not synced accross browsers.

FIXME: doesn't work in a res.config view

Tested on 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d.

Further information and discussion: https://yelizariev.github.io/odoo/module/2015/02/18/last-viewed-records.html
    """,
    'depends' : ['web', 'mail'],
    'data':[
        'views.xml',
        ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'installable': True
}
