{
    'name' : 'Initialization data',
    'version' : '1.0.0',
    'author' : 'IT-Projects LLC, Veronika Kotovich',
    'license': 'GPL-3',
    'website' : 'https://twitter.com/vkotovi4',
    'category' : 'Other',
    'description': """

    """,
    'depends' : ['l10n_sg',
                 'pitch_booking',
                 'sms_sg',
                 'sale_order_hide_tax',
                 'sale_contract_slots',
                 'res_partner_phone',
                 'booking_calendar_analytic',
             ],
    'data':[
        'data.xml',
        'views/view.xml',
        ],
    'installable': True,
    'auto_install': False,
}
