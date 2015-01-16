{
    'name' : 'IM Notifications',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://it-projects.info',
    'description': """
Allows to sent nofitications via IM.

Options for notifications:

* Never
* Only IM (if online)
* IM (if online) + email (if offline)
* IM (if online) + email 
* Only Emails

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['im_chat', 'mail'],
    'data':[
        'im_notif_data.xml',
        'im_notif_views.xml',
        ],
    'installable': True
}
