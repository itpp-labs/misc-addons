# -*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
from import_base import import_base, create_childs

from pandas import merge, DataFrame
from .mapper import *
import subprocess

class import_sugarcrm(import_base):

    TABLE_USER = 'users'
    TABLE_ACCOUNT = 'accounts'
    TABLE_ACCOUNT_LEAD = 'accounts_leads'
    TABLE_ACCOUNT_TAG = 'accounts_tags_'
    TABLE_CONTACT = 'contacts'
    TABLE_CONTACT_COMPANY = 'contacts_companies_'
    TABLE_CONTACT_TAG = 'contacts_tags_'
    TABLE_CASE = 'cases'

    #TABLE_EMPLOYEE = 'Employees'
    #TABLE_OPPORTUNITY = 'Opportunities'
    #TABLE_LEAD = 'Leads'
    #TABLE_STAGE = 'crm_stage'
    #TABLE_ATTENDEE = 'calendar_attendee'
    #TABLE_CALL = 'Calls'
    #TABLE_MEETING = 'Meetings'
    #TABLE_TASK = 'Tasks'
    #TABLE_PROJECT = 'Project'
    #TABLE_PROJECT_TASK = 'ProjectTask'
    #TABLE_BUG = 'Bugs'
    TABLE_NOTE = 'Notes'
    TABLE_NOTE_INTERNAL = 'notes_internal'
    TABLE_EMAIL = 'emails'
    #TABLE_COMPAIGN = 'Campaigns'
    #TABLE_DOCUMENT = 'Documents'
    #TABLE_HISTORY_ATTACHMNET = 'history_attachment'
    


    def initialize(self):
        self.db = MySQLdb.connect(host=self.context.get('db_host'),
                                  port=int(self.context.get('db_port')),
                                  user=self.context.get('db_user'),
                                  passwd=self.context.get('db_passwd'),
                                  db=self.context.get('db_name'),
                                  charset='utf8',
                                  cursorclass=MySQLdb.cursors.DictCursor
                              )
        db_dump_fies = self.context.get('db_dump_fies')
        if db_dump_fies:
            cur = self.db.cursor()
            for f in db_dump_fies:
                print 'load dump', f
                fd = open(f, 'r')
                subprocess.Popen(['mysql',
                                  '-u', self.context.get('db_user'),
                                  '-p{}'.format(self.context.get('db_passwd')),
                                  '-h', self.context.get('db_host'),
                                  '-P', self.context.get('db_port'),
                                  self.context.get('db_name')], stdin=fd).wait()


            cur.close()

    def finalize(self):

        mail_message_obj = self.pool['mail.message']
        ids = self.pool['ir.attachment'].search(self.cr, self.uid, [('res_model_tmp','=','mail.message')])
        for a in self.pool['ir.attachment'].read(self.cr, self.uid, ids, ['id', 'res_id_tmp'], context=self.context):
            if not a['res_id_tmp']:
                continue
            mail_message_obj.write(self.cr, self.uid, [a['res_id_tmp']],
                                   {'attachment_ids':[(4, a['id'])]})


    def get_data(self, table):
        cur = self.db.cursor()
        query = "SELECT * FROM %s" % table
        #query = query + ' order by rand()' # for debug
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        return list(res)

    def get_mapping(self):
        res = [
            self.get_mapping_user(),
            self.get_mapping_account(),
            self.get_mapping_contact(),
            self.get_mapping_case(),
            self.get_mapping_email(),
            self.get_mapping_note_internal(),
            self.get_mapping_note(),
        ]
        return res

    def merge_table_email(self, df, id_on='id'):
#mysql> select bean_module, count(*) from email_addr_bean_rel group by bean_module;
#+-------------+----------+
#| bean_module | count(*) |
#+-------------+----------+
#| Contacts    |     1048 |
#| Leads       |       31 |
#| Prospects   |    20391 |
#| Users       |       33 |
#+-------------+----------+
#4 rows in set (0.21 sec)
        t1 = merge(df,
                   DataFrame(self.get_data('email_addr_bean_rel')),
                   how='left',
                   left_on=id_on,
                   suffixes=('', '_email_addr_bean_rel'),
                   right_on='bean_id')
        t2 = merge(t1,
                   DataFrame(self.get_data('email_addresses')),
                   how='left',
                   left_on = 'email_address_id',
                   suffixes=('', '_email_addresses'),
                   right_on = 'id')

        return t2

    def table_user(self):
        t1 = self.merge_table_email(DataFrame(self.get_data('users')))
        return t1

    def get_mapping_user(self):
        return {
            'name': self.TABLE_USER,
            'table': self.table_user,
             'models':[{
                'model' : 'res.users',
'fields': {
                'id': xml_id(self.TABLE_USER, 'id'),
                'active': lambda record: not record['deleted'], # status == 'Active'
                'name': concat('first_name', 'last_name'),
                 'login': value('user_name', fallback='last_name'),
                 'password' : 'user_hash',
                'company_id/id': const('base.main_company'),
                'alias_name': value('user_name', fallback='last_name', lower=True),
                'email': 'email_address',
             }
}]
            }
    
    def table_account(self):
        t1 = merge(DataFrame(self.get_data('accounts')),
                   DataFrame(self.get_data('accounts_cstm')),
                   left_on='id',
                   right_on='id_c'
        )
        #t1 = t1[:100] # for debug
        return t1

    def get_hook_tag(self, field_name):
        def f(external_values):
            res = []
            value = external_values.get(field_name)
            value = value or ''
            for v in str(value).split(','):
                v = do_clean_sugar(v)
                if v:
                    res.append({field_name:v})
            return res
        return f

    def partner_tag(self, xml_id_prefix, field_name):
        parent = xml_id_prefix + field_name
        return {'model':'res.partner.category',
                'hook':self.get_hook_tag(field_name),
                 'fields': {
                    'id': xml_id(parent, field_name),
                    'name': field_name,
                     'parent_id/id':const('sugarcrm_migration.'+parent),
                    }
                }
    def context_partner(self):
        # you have to modify create and write functions in openerp/addons/base/res/res_partner.py for import optimization
        return {"skip_addr_sync":True}
    def get_mapping_account(self):
        def partner(prefix, suffix):
            return {'model' : 'res.partner',
                 'hook': self.get_hook_ignore_empty('%sfirst_name%s'%(prefix, suffix),
                                                '%slast_name%s'%(prefix, suffix)),
                    'context':self.context_partner,
                 'fields': {
                     'id': xml_id(self.TABLE_ACCOUNT + '_%s%s'%(prefix, suffix), 'id'),
                     'name': concat('%sfirst_name%s'%(prefix, suffix), '%slast_name%s'%(prefix, suffix)),
                     'phone': '%sphone%s'%(prefix, suffix),
                     'mobile': '%smobile%s'%(prefix, suffix),
                     'fax': '%sfax%s'%(prefix, suffix),
                     'email': '%semail%s'%(prefix, suffix),
                     'parent_id/id': xml_id(self.TABLE_ACCOUNT, 'id'),
                     'function': '%sjob_title%s'%(prefix, suffix),
                        'customer': const('1'),
                        'supplier': const('0'),
                    },
                 }
        partner_list = [
            partner('finance_', ''),
            partner('pa_', '_primary_c'),
            partner('pa_', '_secondary_c'),
            partner('', '_primary_c'),
            partner('', '_secondary_c'),
            partner('', '_quantenary_c'),
            partner('', '_other_c'),
            ]
        tag_list = [
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'initial_source_of_referral_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'private_sector_new_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'rtw_organisation_type_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'sales_funnel_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'shenley_holdings_company_new_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'source_of_referral_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'status_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'introduced_by_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'introduced_by_customer_c'),
            self.partner_tag(self.TABLE_ACCOUNT_TAG, 'sister_company_c'),
            ]
            
        return {
            'name': self.TABLE_ACCOUNT,
            'table': self.table_account,
             'dependencies' : [self.TABLE_USER],

            'models': tag_list + [
                # company
                {
             'model' : 'res.partner',
             'context':self.context_partner,
             'fields' :
                {
                'id': xml_id(self.TABLE_ACCOUNT, 'id'),
                 'name': concat('name', 'first_name_c', 'last_name_c'),
                'is_company': const('1'),
                'date': fixdate('date_entered'),
                'active': lambda record: not record['deleted'],
                 'user_id/.id': user_by_login('account_manager_2_c'),
                 'website': first('website', 'website_c'),
                'phone':'company_phone_c',
                'email':first('email_address', 'email_c', lower=True),
                'fax': first('phone_fax', 'fax_c', 'fax_primary_c'),
                 'city': 'company_city_c',
                 'zip': 'company_post_code_c',
                 #'state_id': 'company_region_c',
                 'street': 'company_street_c',
                 'street2': concat('company_street_2_c','company_street_3_c'),
                 'country_id/.id': country_by_name('europe_c'),
                 'opt_out': mapper_int('unsubscribe_c'),
                 'customer': const('1'),
                 'supplier': const('0'),
                 'category_id/id': tags_from_fields(self.TABLE_ACCOUNT_TAG, ['initial_source_of_referral_c', 'private_sector_new_c', 'rtw_organisation_type_c', 'sales_funnel_c', 'shenley_holdings_company_new_c', 'source_of_referral_c', 'status_c', 'introduced_by_c', 'introduced_by_customer_c', 'sister_company_c',]),
                 'comment': ppconcat('website_c'),
             }},
                # realted lead
                {
                'model' : 'crm.lead',
'fields': {
                'id': xml_id(self.TABLE_ACCOUNT_LEAD, 'id'),
                'partner_id/id': xml_id(self.TABLE_ACCOUNT, 'id'),
                 'name': concat('name', 'first_name_c', 'last_name_c'),
                'active': lambda record: not record['deleted'],
                #'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),

                'phone':first('phone_office', 'telephone_c', 'company_phone_c'),
                'email_from':first('email_address', 'email_c', lower=True),
                'fax': first('phone_fax', 'fax_c', 'fax_primary_c'),
                 'probability': map_val('sales_funnel_c', self.map_lead_probability, 0),
                'stage_id/id': map_val('status_c', self.map_lead_stage, 'crm.stage_lead1'),
                'type': map_val('status_c', self.map_lead_type, 'lead'),
                'section_id/id': const('sales_team.section_sales_department'),

                }
}

                ] + partner_list # related contacts
            }


    map_lead_probability = {
        'Lost': 0,
        'Proposal Sent': 50,
        'Prospect Identified': 1,
        'Prospect Qualified': 20,
        'Sales Won': 100,
        'Scheduled': 100, #in sugarcrm: 150,
        'Suspect': 0,
        }
#mysql> select sales_funnel_c, count(*) from accounts_cstm group by sales_funnel_c;
#+---------------------+----------+
#| sales_funnel_c      | count(*) |
#+---------------------+----------+
#| NULL                |     4322 |
#|                     |      144 |
#| Lost                |        1 |
#| Proposal Sent       |        3 |
#| Prospect Identified |        5 |
#| Prospect Qualified  |       20 |
#| Sales Won           |        2 |
#| Scheduled           |        1 |
#| Suspect             |       62 |

    map_lead_stage = {
        '':             'crm.stage_lead7', # Lost
        'Archived':     'crm.stage_lead2', # Dead
        'Dorment':      'crm.stage_lead4',  # Proposition
        'Live Contact': 'crm.stage_lead6',  # Won
        'Pipeline':     'crm.stage_lead5',  # Negotiation
        'Prospect':     'crm.stage_lead1', # New
        }
    map_lead_type = {
        'Dorment':      'opportunity',
        'Live Contact': 'opportunity',
        'Pipeline':     'opportunity',
        }
#mysql> select status_c, count(*) from accounts_cstm group by status_c;
#+---------------+----------+
#| status_c      | count(*) |
#+---------------+----------+
#| NULL          |      210 |
#|               |      655 |
#| Archived      |       84 |
#| Dorment       |      101 |
#| Live Contract |       73 |
#| Pipeline      |      390 |
#| Prospect      |     3047 |
#+---------------+----------+

    def table_contact(self):
        t1 = merge(DataFrame(self.get_data('contacts')),
                   DataFrame(self.get_data('contacts_cstm')),
                   left_on='id',
                   right_on='id_c'
        )

        t2 = self.merge_table_email(t1)
        #t2 = t2[:10] # for debug
        return t2


    def get_mapping_contact(self):
        tag_list = [
            self.partner_tag(self.TABLE_CONTACT_TAG, 'agreed_commission_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'agreed_introducer_commission_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'ambassador_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'consultant_type_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'consultant_type_other_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'england_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'ethnicity_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'europe_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'first_language_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'gender_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'other_languages_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'religion_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'role_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'role_type_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'specialism_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'status_live_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'status_live_new_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'trainer_type_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'training_experience_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'willing_to_travel_c'),
            self.partner_tag(self.TABLE_CONTACT_TAG, 'skill_set_c'),
            ]

        def company(field_name):
            return {'model':'res.partner',
                    'hook':self.get_hook_ignore_empty(field_name),
                    'fields': {
                        'id': xml_id(self.TABLE_CONTACT_COMPANY, field_name),
                        'name': field_name,
                        'is_company': const('1'),
                        'customer': const('0'),
                        'supplier': const('1'),
                        }
                    }
        return {
            'name': self.TABLE_CONTACT,
            'table': self.table_contact,
             'dependencies' : [self.TABLE_USER],
             'models':tag_list + [company('company_name_c')] + [{
                'model' : 'res.partner',
'fields': {
                'id': xml_id(self.TABLE_CONTACT, 'id'),
                 'name': concat('title', 'first_name', 'last_name'),
                 'parent_id/id': xml_id(self.TABLE_CONTACT_COMPANY, 'company_name_c'),

                'create_date': 'date_entered',
                'write_date': 'date_modified',
                'active': lambda record: not record['deleted'],
                 #'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),

                'city': 'city_c',
                 'street': 'company_street_c',
                 'street2': concat('company_street_2_c','company_street_3_c'),
                 'zip': 'company_post_code_c',

                'phone':first('company_phone_c', 'home_phone_c', 'phone_home', 'phone_work', 'phone_other', 'home_telephone_c', 'business_telephone_c'),
                'mobile':first('phone_mobile', 'personal_mobile_phone_c'),
                'email':first('email_c', 'email_address', 'personal_email_c', 'business_email_c', 'other_email_c',  'email_2_c'),
                 'website': first('website', 'website_c'),

                'fax': first('phone_fax', 'company_fax_c'),
                 'customer': const('0'),
                 'supplier': const('1'),

                  'category_id/id': tags_from_fields(self.TABLE_CONTACT_TAG, ['agreed_commission_c', 'agreed_introducer_commission_c', 'ambassador_c', 'consultant_type_c', 'consultant_type_other_c', 'england_c', 'ethnicity_c', 'europe_c', 'first_language_c', 'gender_c', 'other_languages_c', 'religion_c', 'role_c', 'role_type_c', 'skill_set_c', 'specialism_c', 'status_live_c', 'status_live_new_c', 'trainer_type_c', 'training_experience_c', 'willing_to_travel_c', ]),

                 'comment': ppconcat(
                        'description',
                        'phone_home',
                        'phone_mobile',
                        'phone_work',
                        'phone_other',
                        'phone_fax',
                        'personal_email_c',
                        'business_email_c',
                        'other_email_c',
                        'home_telephone_c',
                        'business_telephone_c',
                        'personal_mobile_phone_c',
                        'personal_telephone_c',
                        'home_phone_c',
                        'mobile_phone_c',
                        'other_phone_c',
                        'email_c',
                        'email_2_c',
                        'company_phone_c',
                        'company_mobile_phone_c',
                        'company_fax_c',
                        'company_phone_other_c',
                        'company_email_c',
                        'prg_email_issued_c',
                        'email_address_permanent_c',
                        'prg_email_c',
                        'cjsm_email_address_c',
                            )
             }
}]
        }
    def table_case(self):
        t1 = merge(DataFrame(self.get_data('cases')),
                   DataFrame(self.get_data('cases_cstm')),
                   left_on='id',
                   right_on='id_c'
        )
        #t1 = t1[:10] # for debug
        return t1


    case_priority_mapping = {
                'P1': '0',
                'P2': '1',
                'P3': '2'
        }

    def get_mapping_case(self):
#mysql> select case_status_c, count(*) from cases_cstm group by case_status_c;
#+----------------------+----------+
#| case_status_c        | count(*) |
#+----------------------+----------+
#| NULL                 |        2 |
#|                      |       40 |
#| Awaiting Payment     |       10 |
#| Cancelled            |      182 |
#| Completed            |      339 |
#| Deferred             |      125 |
#| Live                 |       25 |
#| Lost                 |      419 |
#| Pipeline             |       60 |
#| Pipeline - Proactive |       73 |
#| Provisional          |        2 |
#| To be Invoiced       |        7 |
#+----------------------+----------+


        return {
            'name': self.TABLE_CASE,
            'table': self.table_case,
             'dependencies' : [
                 self.TABLE_USER,
                 self.TABLE_ACCOUNT,
                 self.TABLE_CONTACT,
                 #self.TABLE_LEAD
             ],
             'models':[{
                'model' : 'project.task',
'fields': {
                'id': xml_id(self.TABLE_CASE, 'id'),
                 'name': concat('case_number','case_number_c', 'name', delimiter='-'),
                 'create_date': 'date_entered',
                'active': lambda record: not record['deleted'],
                 'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/id': xml_id(self.TABLE_ACCOUNT, 'account_id'),
                 #'supplier_id/id': xml_id(self.TABLE_ACCOUNT, 'account_id'),
                 'kanban_state': 'TODO',
                 'priority': map_val('priority', self.case_priority_mapping, '1'),

                 'description': ppconcat(
                     'description',

#'id',#                               | char(36)         |          1284 |
#'name',#                             | varchar(255)     |          1273 |
#'date_entered',#                     | datetime         |          1284 |
#'date_modified',#                    | datetime         |          1284 |
#'modified_user_id',#                 | char(36)         |          1284 |
#'created_by',#                       | char(36)         |          1284 |
#'description',#                      | text             |            23 |
#'deleted',#                          | tinyint(1)       |            56 |
#'assigned_user_id',#                 | char(36)         |           161 |
'case_number',#                      | int(11)          |          1284 |
'type',#                             | varchar(255)     |            24 |
'status',#                           | varchar(25)      |            28 |
'priority',#                         | varchar(25)      |            28 |
#'account_id',#                       | char(36)         |          1222 |
#'id_c',#                             | char(36)         |          1284 |
'case_number_c',#                    | varchar(50)      |           164 |
'product_area_c',#                   | varchar(100)     |          1204 |
'product_type_c',#                   | varchar(100)     |          1100 |
'start_date_c',#                     | date             |           395 |
'end_date_c',#                       | date             |           295 |
'high_level_requirement_c',#         | text             |          1013 |
'special_notes_c',#                  | text             |           704 |
#'account_id_c',#                     | char(36)         |          1252 |
#'contact_id_c',#                     | char(36)         |           437 |
#'contact_id1_c',#                    | char(36)         |            32 |
'other_consultant_c',#               | varchar(100)     |            27 |
'primary_contact_c',#                | varchar(100)     |          1076 |
'secondary_contact_c',#              | varchar(100)     |           163 |
'contact_other_1_c',#                | varchar(100)     |             2 |
'contact_other_2_c',#                | varchar(100)     |             1 |
'contact_other_3_c',#                | varchar(100)     |             1 |
'primary_role_c',#                   | varchar(100)     |           696 |
'secondary_role_c',#                 | varchar(100)     |            65 |
'primary_email_c',#                  | varchar(100)     |           803 |
'secondary_email_c',#                | varchar(100)     |           102 |
'secondary_mobile_c',#               | varchar(50)      |            27 |
'primary_mobile_c',#                 | varchar(50)      |           150 |
'primary_phone_c',#                  | varchar(50)      |           611 |
'secondary_phone_c',#                | varchar(100)     |            81 |
'notes_c',#                          | text             |            10 |
'role_1_c',#                         | varchar(100)     |             1 |
'case_status_c',#                    | varchar(100)     |          1242 |
'source_of_referral_c',#             | varchar(100)     |          1014 |
'case_manager_c',#                   | varchar(100)     |          1138 |
'probability_of_closing_c',#         | varchar(100)     |          1284 |
'potential_value_of_contract_c',#    | varchar(100)     |            21 |
'involvement_with_case_c',#          | varchar(200)     |            97 |
'case_participant_c',#               | varchar(50)      |           132 |
'participant_email_c',#              | varchar(50)      |            50 |
'participant_phone_c',#              | varchar(25)      |            41 |
'contact_directly_c',#               | tinyint(1)       |            14 |
'case_participant_2_c',#             | varchar(100)     |           101 |
'participant_phone_2_c',#            | varchar(100)     |            31 |
'participant_email_2_c',#            | varchar(100)     |            41 |
'participant_role_c',#               | varchar(200)     |            65 |
'participant_role_2_c',#             | varchar(200)     |            50 |
'contact_directly_2_c',#             | tinyint(1)       |            11 |
'case_participant_3_c',#             | varchar(100)     |            44 |
'participant_phone_3_c',#            | varchar(100)     |             5 |
'participant_email_3_c',#            | varchar(100)     |             9 |
'participant_role_3_c',#             | varchar(200)     |            11 |
'contact_directly_3_c',#             | tinyint(1)       |             2 |
'parent_type',#                      | varchar(100)     |          1263 |
'parent_id',#                        | varchar(36)      |            51 |
'value_of_case_c',#                  | varchar(100)     |           718 |
'contact_id2_c',#                    | char(36)         |            39 |
'contact_id3_c',#                    | char(36)         |            16 |
'internal_proof_reader_c',#          | varchar(100)     |            12 |
'primary_date_c',#                   | date             |             6 |
'secondary_date_c',#                 | date             |             4 |
'internal_date_c',#                  | date             |             2 |
'reason_lost_c',#                    | varchar(100)     |           233 |
'invoiced_value_of_case_c',#         | varchar(25)      |           328 |
'business_type_c',#                  | varchar(100)     |          1140 |
'support_case_manager_c',#           | varchar(100)     |           522 |
'case_manager_2_c',#                 | varchar(100)     |           247 |
'probability_of_closing_2_c',#       | varchar(100)     |          1052 |
'contact_id4_c',#                    | char(36)         |            22 |
'estimated_close_date_c',#           | varchar(100)     |          1284 |
'production_funnel_c',#              | varchar(100)     |            34 |

                                     ),
             }
}]
                    }

    def table_filter_modules(self, t, field_name='bean_module'):
        newt = t[(t[field_name] == 'Accounts')|
                (t[field_name] == 'Cases')|
                (t[field_name] == 'Contacts')|
                (t[field_name] == 'Notes')|
                (t[field_name] == 'Emails')
                ]
        return newt

    def table_email(self):
        t1 = merge(DataFrame(self.get_data('emails')),
                   DataFrame(self.get_data('emails_text')),
                   how='left',
                   left_on='id',
                   right_on='email_id'
        )
        t2 = merge(t1,
                   DataFrame(self.get_data('emails_beans')),
                   how='left',
                   left_on='id',
                   right_on='email_id',
                   suffixes = ('', '_emails_beans')
        )
        t3 = self.table_filter_modules(t2)
        #t3 = t3[:100] # for debug
        return t3

    map_to_model = {
        'Accounts': 'crm.lead',
        'Cases': 'project.task',
        'Contacts': 'res.partner',
        'Prospects': 'TODO',
        'Emails': 'mail.message',
        #'Notes': 'ir.attachment',
    }
    map_to_table = {
        'Accounts': TABLE_ACCOUNT_LEAD,
        'Cases': TABLE_CASE,
        'Contacts': TABLE_CONTACT,
        'Prospects': 'TODO',
        'Emails': TABLE_EMAIL,
        #'Notes': TABLE_NOTE,
    }
#mysql> select parent_type, count(*) from notes group by parent_type;
#+-------------+----------+
#| parent_type | count(*) |
#+-------------+----------+
#| NULL        |      604 |
#| Accounts    |     6385 |
#| Cases       |    12149 |
#| Contacts    |       41 |
#| Emails      |    12445 |
#| Leads       |      355 |
#| Meetings    |        2 |
#+-------------+----------+
#7 rows in set (0.30 sec)
#


    def get_mapping_email(self):
# mysql> select bean_module, count(*) from emails_beans group by bean_module;
# +---------------+----------+
# | bean_module   | count(*) |
# +---------------+----------+
# | Accounts      |      182 |
# | Cases         |     1746 |
# | Contacts      |      493 |
# | Leads         |      102 |
# | Opportunities |        1 |
# | Prospects     |    16819 |
# +---------------+----------+
# 6 rows in set (0.56 sec)
        return {
            'name': self.TABLE_EMAIL,
            'table': self.table_email,
            'dependencies' : [
                self.TABLE_USER,
                self.TABLE_ACCOUNT,
                self.TABLE_CONTACT,
                self.TABLE_CASE,
                #self.TABLE_LEAD,
                #self.TABLE_OPPORTUNITY,
                #self.TABLE_MEETING,
                #self.TABLE_CALL
            ],
             'models':[{
                'model' : 'mail.message',
'fields': {
                'id': xml_id(self.TABLE_EMAIL, 'id'),
                 'type':const('email'),
                 #mysql> select type, count(*) from emails group by type;
                 #+----------+----------+
                 #| type     | count(*) |
                 #+----------+----------+
                 #| archived |    17119 |
                 #| draft    |        8 |
                 #| inbound  |     3004 |
                 #| out      |       75 |
                 #+----------+----------+
                 #4 rows in set (0.76 sec)

                 'email_from': 'from_addr_name',
                 'reply_to': 'reply_to_addr',
                 #'same_thread': 'TODO',
                 'author_id/id': user2partner(self.TABLE_USER, 'created_by'),
                 #'partner_ids' #many2many
                 #attachment_ids' #many2many
                 #'parent_id': 'TODO',
                 'model': map_val('bean_module', self.map_to_model),
                 'res_id': res_id(map_val('bean_module', self.map_to_table), 'bean_id'),
                 #record_name
                 'subject':'name',
                 'date':'date_sent',
                 'message_id': 'message_id',
                 'body': first('description_html', 'description'),
                 'subtype_id/id':const('mail.mt_comment'),
                'notified_partner_ids/.id': emails2partners('to_addrs'),


                 #'state' : const('received'),
                 #'email_to': 'to_addrs_names',
                 #'email_cc': 'cc_addrs_names',
                 #'email_bcc': 'bcc_addrs_names',
                 #'partner_id/.id': 'partner_id/.id',
                 #'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                    }
}]
                    }

    def table_note(self):
        t = DataFrame(self.get_data('notes'))
        t = self.table_filter_modules(t, 'parent_type')
        t = t.dropna(subset=['filename'])
        #t = t[:10] # for debug
        return t

    def table_note_internal(self):
        t = DataFrame(self.get_data('notes'))
        t = self.table_filter_modules(t, 'parent_type')
        t = t[(t['parent_type'] != 'Emails')]
        #t = t[:100] # for debug
        return t

    def get_id_model(self, external_values, field_name='parent_id'):
        id = res_id(map_val('parent_type', self.map_to_table), field_name)
        id.set_parent(self)
        model = map_val('parent_type', self.map_to_model)
        return id(external_values), model(external_values)

    def hook_note(self, external_values):
        parent_type = external_values.get('parent_type')
        contact_id = external_values.get('contact_id')
        if parent_type == 'Accounts' and contact_id:
            external_values['parent_type'] = 'Contacts'
            id,model = self.get_id_model(external_values, field_name='contact_id')
            if id:
                #print 'note Accounts fixed to Contacts'
                external_values['res_id'] = id
                external_values['res_model'] = model
                return external_values
            external_values['parent_type'] = parent_type

        id,model = self.get_id_model(external_values)
        if not id:
            #print 'Note not found', parent_type, external_values.get('parent_id')
            return None
        else:
            #print 'Note     FOUND', parent_type, external_values.get('parent_id')
            pass
        external_values['res_id'] = id
        external_values['res_model'] = model
        return external_values

    map_note_to_table = {
        'Emails': TABLE_EMAIL
        }
    def get_mapping_note(self):
        return {
            'name': self.TABLE_NOTE,
            'table': self.table_note,
            'dependencies' : [self.TABLE_EMAIL,
                              self.TABLE_NOTE_INTERNAL,
                          ],
            'models':[{
                'model': 'ir.attachment',
                'hook': self.hook_note,
'fields': {
                'id': xml_id(self.TABLE_NOTE, 'id'),
                'name':'filename',
                'res_model': 'res_model',
                'res_id': 'res_id',
                'res_model_tmp': const('mail.message'),
                'res_id_tmp': res_id(map_val('parent_type', self.map_note_to_table, default=self.TABLE_NOTE_INTERNAL), 'id'),

                'store_fname': 'filename',
                'type':const('binary'),
                'description': 'description',
                'create_date': 'date_entered',
                'create_uid/id': xml_id(self.TABLE_USER, 'create_by'),
                'company_id/id': const('base.main_company'),
            }
}]
        }
    def get_mapping_note_internal(self):
        return {
            'name': self.TABLE_NOTE_INTERNAL,
            'table': self.table_note_internal,
            'dependencies' : [self.TABLE_EMAIL,
                          ],
            'models':[{
                'model': 'mail.message',
                'hook': self.hook_note,
'fields': {
                'id': xml_id(self.TABLE_NOTE_INTERNAL, 'id'),


                'subject':concat('name', 'filename', 'date_entered', delimiter=' * '),
                'body': 'description',
                'model': 'res_model',
                 'res_id': 'res_id',

                 'type':const('email'),
                'date': 'date_entered',
                'author_id/id': user2partner(self.TABLE_USER, 'created_by'),
                 #'subtype_id/id':const('mail.mt_comment'),
            }
}]
        }
    def get_mapping_history_attachment(self):
        # is not used
        res.append({
            'name': self.TABLE_HISTORY_ATTACHMNET,
             'model' : 'ir.attachment',
             'dependencies' : [self.TABLE_USER, self.TABLE_ACCOUNT, self.TABLE_CONTACT, self.TABLE_LEAD, self.TABLE_OPPORTUNITY, self.TABLE_MEETING, self.TABLE_CALL, self.TABLE_EMAIL],
             'hook' : import_history,
             'models':[{
'fields': {
                 'name':'name',
                 'user_id/id': ref(self.TABLE_USER, 'created_by'),
                 'description': ppconcat('description', 'description_html'),
                 'res_id': 'res_id',
                 'res_model': 'model',
                 'partner_id/.id' : 'partner_id/.id',
                 'datas' : 'datas',
                 'datas_fname' : 'datas_fname'
             }
}]
                    })
    def get_mapping_bug():
        # is not used
        return {
            'name': self.TABLE_BUG,
             'model' : 'project.issue',
             'dependencies' : [self.TABLE_USER],
             'models':[{
'fields': {
                 'name': concat('bug_number', 'name', delimiter='-'),
                 'project_id/id': call(get_bug_project_id, 'sugarcrm_bugs'),
                 'categ_id/id': call(get_category, 'project.issue', value('type')),
                 'description': ppconcat('description', 'source', 'resolution', 'work_log', 'found_in_release', 'release_name', 'fixed_in_release_name', 'fixed_in_release'),
                 'priority': get_project_issue_priority,
                 'state': map_val('status', project_issue_state),
                 'assigned_to/id' : ref(self.TABLE_USER, 'assigned_user_id'),
             }
}]
            }
    def get_mapping_project(self):
        # is not used
        return {
            'name': self.TABLE_PROJECT,
             'model' : 'project.project',
             'dependencies' : [self.TABLE_CONTACT, self.TABLE_ACCOUNT, self.TABLE_USER],
             'hook' : import_project,
             'models':[{
'fields': {
                 'name': 'name',
                 'date_start': 'estimated_start_date',
                 'date': 'estimated_end_date',
                 'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/.id': 'partner_id/.id',
                 'contact_id/.id': 'contact_id/.id',
                 'state': map_val('status', project_state)
             }
}]
            }
    def get_mapping_project_task(self):
        # is not used
        return {
            'name': self.TABLE_PROJECT_TASK,
             'model' : 'project.task',
             'dependencies' : [self.TABLE_USER, self.TABLE_PROJECT],
             'models':[{
'fields': {
                 'name': 'name',
                 'date_start': 'date_start',
                 'date_end': 'date_finish',
                 'project_id/id': ref(self.TABLE_PROJECT, 'project_id'),
                 'planned_hours': 'estimated_effort',
                 'priority': get_project_task_priority,
                 'description': ppconcat('description','milestone_flag', 'project_task_id', 'task_number', 'percent_complete'),
                 'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/id': 'partner_id/id',
                 'contact_id/id': 'contact_id/id',
                 'state': map_val('status', project_task_state)
             }
}]
            }
    def get_mapping_task(self):
        # is not used
        return {
            'name': self.TABLE_TASK,
             'model' : 'crm.meeting',
             'dependencies' : [self.TABLE_CONTACT, self.TABLE_ACCOUNT, self.TABLE_USER],
             'hook' : import_task,
             'models':[{
'fields': {
                 'name': 'name',
                 'date': 'date',
                 'date_deadline': 'date_deadline',
                 'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                 'categ_id/id': call(get_category, 'crm.meeting', const('Tasks')),
                 'partner_id/id': related_ref(self.TABLE_ACCOUNT),
                 'partner_address_id/id': ref(self.TABLE_CONTACT,'contact_id'),
                 'state': map_val('status', task_state)
             }
}]
            }
    def get_mapping_call(self):
        # is not used
        return {
            'name': self.TABLE_CALL,
             'model' : 'crm.phonecall',
             'dependencies' : [self.TABLE_ACCOUNT, self.TABLE_CONTACT, self.TABLE_OPPORTUNITY, self.TABLE_LEAD],
             'models':[{
'fields': {
                 'name': 'name',
                 'date': 'date_start',
                 'duration': call(get_float_time, value('duration_hours'), value('duration_minutes')),
                 'user_id/id':  ref(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/id': related_ref(self.TABLE_ACCOUNT),
                 'partner_address_id/id': related_ref(self.TABLE_CONTACT),
                 'categ_id/id': call(get_category, 'crm.phonecall', value('direction')),
                 'opportunity_id/id': related_ref(self.TABLE_OPPORTUNITY),
                 'description': ppconcat('description'),
                 'state': map_val('status', call_state)
             }
}]
            }
    def get_mapping_meeting(self):
        # is not used
        return {
            'name': self.TABLE_MEETING,
             'model' : 'crm.meeting',
             'dependencies' : [self.TABLE_CONTACT, self.TABLE_OPPORTUNITY, self.TABLE_LEAD, self.TABLE_TASK],
             'hook': import_meeting,
             'models':[{
'fields': {
                 'name': 'name',
                 'date': 'date_start',
                 'duration': call(get_float_time, value('duration_hours'), value('duration_minutes')),
                 'location': 'location',
                 'attendee_ids/id':'attendee_ids/id',
                 'alarm_id/id': call(get_alarm_id, value('reminder_time')),
                 'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/id': related_ref(self.TABLE_ACCOUNT),
                 'partner_address_id/id': related_ref(self.TABLE_CONTACT),
                 'state': map_val('status', meeting_state)
             }
}]
            }
    def get_mapping_opportunity(self):
        # is not used
        return {
            'name': self.TABLE_OPPORTUNITY,
             'model' : 'crm.lead',
             'dependencies' : [self.TABLE_USER, self.TABLE_ACCOUNT, self.TABLE_CONTACT,self.TABLE_COMPAIGN],
             'hook' : import_opp,
             'models':[{
'fields': {
                 'name': 'name',
                 'probability': 'probability',
                 'partner_id/id': refbyname(self.TABLE_ACCOUNT, 'account_name', 'res.partner'),
                 'title_action': 'next_step',
                 'partner_address_id/id': 'partner_address_id/id',
                 'planned_revenue': 'amount',
                 'date_deadline': 'date_closed',
                 'user_id/id' : ref(self.TABLE_USER, 'assigned_user_id'),
                 'stage_id/id' : get_opportunity_status,
                 'type' : const('opportunity'),
                 'categ_id/id': call(get_category, 'crm.lead', value('opportunity_type')),
                 'email_from': 'email_from',
                 'state': map_val('status', opp_state),
                 'description' : 'description',
             }
}]
            }
    def get_mapping_compaign(self):
        # is not used
        return {
            'name': self.TABLE_COMPAIGN,
             'model' : 'crm.case.resource.type',
             'models':[{
'fields': {
                 'name': 'name',
             }
}]
            }
    def get_mapping_employee(self):
        # is not used
        return {
            'name': self.TABLE_EMPLOYEE,
             'model' : 'hr.employee',
             'dependencies' : [self.TABLE_USER],
             'models':[{
'fields': {
                 'resource_id/id': get_ressource,
                 'name': concat('first_name', 'last_name'),
                 'work_phone': 'phone_work',
                 'mobile_phone':  'phone_mobile',
                 'user_id/id': ref(self.TABLE_USER, 'id'),
                 'address_home_id/id': get_user_address,
                 'notes': ppconcat('messenger_type', 'messenger_id', 'description'),
                 'job_id/id': get_job_id,
                 'work_email' : 'email1',
                 'coach_id/id_parent' : 'reports_to_id',
             }
}]
            }
