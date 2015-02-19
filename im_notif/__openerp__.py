{
    'name' : 'IM Notifications',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """
Allows to sent nofitications via IM.

Options for notifications:

* Never
* Only IM (if online)
* IM (if online) + email (if offline)
* IM (if online) + email 
* Only Emails

Tested on Odoo 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d

Further information and discussion: https://yelizariev.github.io/odoo/module/2015/02/18/im-notifications.html
    """,
    'depends' : ['im_chat', 'mail'],
    'data':[
        'im_notif_data.xml',
        'im_notif_views.xml',
        ],
    'installable': True
}
