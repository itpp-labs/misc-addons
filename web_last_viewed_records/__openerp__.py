{
    'name' : 'Last viewed records',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://it-projects.info',
    'description': """
The idea is taken from SugarCRM's "Last viewed" feature.

This module doesn't affect on server performance, because it uses browser's localStorage to save history. But dissadvantage is that history is not synced accross browsers.

Tested on 8.0 ab7b5d7.

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
