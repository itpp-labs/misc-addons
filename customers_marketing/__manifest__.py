##########################################################################
#
#   Copyright (c) 2016-Present Techspawn Solutions Pvt. Ltd.
# (<https://techspawn.com/>)
#
##########################################################################

{
    'name': 'Customer Marketing',
    'version': '10.0.1.0.0',
    'category': 'Custom',
    'sequence': 10,
    'author': 'Techspawn Solutions Pvt. Ltd.',
    'website': 'http://www.techspawn.com',
    'description': """

Customer Marketing
=========================

----------------------------------------------------------------------------------------------------------
    """,
    'depends': ['base',
                'sale',
                'base_details',
                'accessories',
                'apparel',
                'major_unit',
                'product_review',
                'woo_product_detail',
                'product_rewards',
                'sales_reward',

                ],
    'data': [
              'views/product_custom_view.xml',
              'wizard/create_customer_ride_view.xml',
              'views/customer_custom_view.xml',
              'views/customer_ride_view.xml',
              'views/product_vehicle_details_view.xml',
              'data/misc_charge_demo.xml',


    ],
    'js': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
