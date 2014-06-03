{
    'name' : 'Check quantity on stock moves',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Stock',
    'website' : 'https://it-projects.info',
    'description': """
* Show warning message, if there are not enough items for stock move
* Show shortage at move list
    """,
    'depends' : ['stock'],
    'data':[
        'views.xml',
        ],
    'installable': True
}
