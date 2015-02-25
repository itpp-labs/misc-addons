{
    'name' : 'Search partner by company fields',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """
Search partner by company fields. It uses only related fields like this:

    p_FIELD_NAME = fields.TYPE(related='parent_id.FIELD_NAME', string='Parent FIELD')

Check models.py file to find list of related fields.

Technically modules updates search domain as follows:

    [..., ('category_id', OPERATOR, VALUE), ...]

    ->

    [..., '|', ('p_category_id', OPERATOR, VALUE), ('category_id', OPERATOR, VALUE), ...]


Tested on Odoo 8.0 ea60fed97af1c139e4647890bf8f68224ea1665b
    """,
    'depends' : ['base'],
    'data':[
        'views.xml',
        ],
    'installable': True
}
