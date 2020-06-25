{
    'name': "Service",

    'summary': """Vehicle Service System""",
    'category': 'Custom',
    'sequence': 1,
    'description': """
        Customer Vehicle Repair Shop Management System..
    """,

    'author': "Techspawn",
    'website': "http://www.techspawn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['base', 'calendar', 'hr', 'mrp'],

    # always loaded

    # NOTE please dont change the sequence of the xml files
    'data': [
        # 'data/ir_sequence_data.xml',
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'wizard/create_pickup.xml',
        # 'wizard/create_inspection.xml',
        # 'wizard/service_confirm_suggested_job_views.xml',
        # 'wizard/drm_workcenter_block_view.xml',
        # 'wizard/select_recall_job.xml',
        # 'views/calendar.xml',
        # 'views/inspection.xml',
        # 'views/sequence_data.xml',
        # 'views/pickup.xml',
        # 'report/service_report_templates.xml',
        # 'report/service_report.xml',
        # 'views/service_template.xml',
        # 'views/service_slots.xml',
        # 'views/standard_bundle.xml',
        # 'views/service.xml',
        # 'views/work_order.xml',
        # 'views/mechanic.xml',
        # 'views/standard_job_views.xml',
        # 'views/support.xml',
        # 'views/settings.xml',
        # 'views/add_lifts.xml',
        # 'views/pickup_email_template.xml',
        # 'views/pdi.xml',
        # 'views/comeback.xml',
        # 'views/service_dashboard.xml',
        # 'views/recalls.xml',
        # 'views/service_mail.xml',
        # 'views/service_scheduler.xml',
        # 'views/service_remainder.xml',
        'data/dashboard.xml',
        # 'report/reports_service.xml',
        # 'data/drm_data.xml',
        # 'data/hr_demo_data.xml',
        # 'data/lift_data.xml',
        # 'views/mailing.xml',
        # 'views/notification.xml',
        # 'views/opportunity_pipeline.xml',
    ],

    'external_dependencies': {

    },
    'qweb': [
        "static/src/xml/service_team_dashboard.xml",
        "static/src/xml/service_cal.xml",
        # "static/src/xml/repair_dashboard.xml",
        "static/src/xml/service_dashboard.xml",
    ],

    #Dashboard upper part
    # 'qweb': [
    #     # "static/src/xml/service_team_dashboard.xml",
    # ],
    # only loaded in demonstration mode
    'demo': [
        'data/drm_data.xml',
        'data/lift_data.xml',
    ],
    'css': ['static/src/css/sales_team.css'],
    'application': True,
    'installable': True,
    'auto_install': True,
}
