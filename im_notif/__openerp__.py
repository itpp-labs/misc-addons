{
    'name' : 'IM Notifications',
    'version': '1.0.1',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category' : 'Tools',
    'website' : 'https://twitter.com/yelizariev',
    'price': 9.00,
    'currency': 'EUR',
    'depends' : ['im_chat', 'mail'],
    'images': ['images/my-pref.png'],
    'data':[
        'im_notif_data.xml',
        'im_notif_views.xml',
        ],
    'installable': True,
    'uninstall_hook': 'pre_uninstall',
}
