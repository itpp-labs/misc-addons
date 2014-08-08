import MySQLdb
import MySQLdb.cursors
from import_base import import_base

from pandas import merge, DataFrame
from .mapper import *
import subprocess

class import_sugarcrm(import_base):

    TABLE_USER = 'users'
    TABLE_ACCOUNT = 'accounts'
    TABLE_CONTACT = 'contacts'
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
            self.get_mapping_note(),
        ]
        return res

    def merge_table_email(self, df, id_index='id'):
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
                   left_index=id_index,
                   suffixes=('', '_email_addr_bean_rel'),
                   right_index='bean_id')
        t2 = merge(t1,
                   DataFrame(self.get_data('email_addresses')),
                   left_index = 'email_address_id',
                   suffixes=('', '_email_addresses'),
                   right_index = 'id')
        return t2

    def table_user(self):
        t1 = self.merge_table_email(DataFrame(self.get_data('users')))
        return t1

    def get_mapping_user(self):
        return {
            'name': self.TABLE_USER,
            'table': self.table_user,
             'model' : 'res.users',
             'map' : {
                'id': xml_id(self.TABLE_USER, 'id'),
                'active': lambda record: not record['deleted'], # status == 'Active'
                'name': concat('first_name', 'last_name'),
                 'login': value('user_name', fallback='last_name'),
                 'password' : 'user_hash',
                'company_id/id': const('base.main_company'),
                'alias_name': value('user_name', fallback='last_name', lower=True),
                'email': 'email_address',
             }
            }
    
    def table_account(self):
        t1 = merge(DataFrame(self.get_data('accounts')),
                   DataFrame(self.get_data('accounts_cstm')),
                   left_index='id',
                   right_index='id_c'
        )
        #t1 = t1[:10] # for debug
        return t1
    def get_mapping_account(self):
        return {
            'name': self.TABLE_ACCOUNT,
            'table': self.table_account,
             'model' : 'res.partner',
             'dependencies' : [self.TABLE_USER],
             'map' : {
                'id': xml_id(self.TABLE_ACCOUNT, 'id'),
                 'name': concat('name', 'first_name_c', 'last_name_c'),
                'date': fixdate('date_entered'),
                'active': lambda record: not record['deleted'],
                 'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),
                 'website': first('website', 'website_c'),
                'phone':first('phone_office', 'telephone_c', 'company_phone_c', 'phone_primary_c'),
                'mobile':first('mobile_phone_primary_c', 'mobile_phone_other_c'),
                'email':first('email_address', 'email_c', 'email_primary_c', 'email_other_c', lower=True),
                'fax': first('phone_fax', 'fax_c', 'fax_primary_c'),
                 'ref': 'sic_code',
                 'customer': const('1'),
                 'supplier': const('0'),
                 #'parent_id/id' : xml_id(self.TABLE_ACCOUNT, 'parent_id'),
    
    
                 'comment': ppconcat('description', 'employees', 'ownership', 'annual_revenue', 'rating', 'industry', 'ticker_symbol',
    #'id_c', #                             |          4560 |
    'company_c', #                        |             7 |
    #'website_c', #                        |          2225 |
    'address_c', #                        |             5 |
    'telephone_c', #                      |            17 |
    'fax_c', #                            |            18 |
    'title_c', #                          |             7 |
    'first_name_c', #                     |            19 |
    'last_name_c', #                      |            19 |
    'email_c', #                          |            18 |
    'department_c', #                     |            18 |
    'job_title_c', #                      |            15 |
    'case_history_c', #                   |             2 |
    'associated_income_c', #              |            47 |
    'filed_complaints_c', #               |             2 |
    'meeting_history_c', #                |             1 |
    'group_company_c', #                  |             7 |
    'contract_signed_c', #                |             5 |
    'telephone_2_c', #                    |             1 |
    'preffered_consultant_1_c', #         |          4560 |
    'preferred_consultant_2_c', #         |          4560 |
    'company_phone_c', #                  |          1127 |
    'company_street_c', #                 |          3022 |
    'company_street_2_c', #               |          1586 |
    'company_street_3_c', #               |           644 |
    'company_city_c', #                   |          2635 |
    'company_post_code_c', #              |          2368 |
    'title_primary_c', #                  |           358 |
    'first_name_primary_c', #             |          3608 |
    'last_name_primary_c', #              |          3235 |
    'post_nominal_titles_primary_c', #    |             4 |
    'job_title_primary_c', #              |          2788 |
    'department_primary_c', #             |           311 |
    'email_primary_c', #                  |          2953 |
    'phone_primary_c', #                  |          2111 |
    'ext_primary_c', #                    |            27 |
    'mobile_phone_primary_c', #           |           363 |
    'fax_primary_c', #                    |           185 |
    'title_secondary_c', #                |           125 |
    'first_name_secondary_c', #           |          1069 |
    'last_name_secondary_c', #            |          1057 |
    'post_nominal_titles_secondary_c', #  |             1 |
    'job_title_secondary_c', #            |          1026 |
    'department_secondary_c', #           |           115 |
    'email_secondary_c', #                |           932 |
    'phone_secondary_c', #                |           803 |
    'ext_secondary_c', #                  |            11 |
    'mobile_phone_secondary_c', #         |            83 |
    'fax_secondary_c', #                  |            16 |
    'title_other_c', #                    |            45 |
    'first_name_other_c', #               |           475 |
    'last_name_other_c', #                |           471 |
    'post_nominal_titles_other_c', #      |             3 |
    'job_title_other_c', #                |           463 |
    'department_other_c', #               |            72 |
    'email_other_c', #                    |           404 |
    'phone_other_c', #                    |           332 |
    'ext_other_c', #                      |            27 |
    'mobile_phone_other_c', #             |            49 |
    'fax_other_c', #                      |            15 |
    'unsubscribe_c', #                    |           107 |
    'status_c', #                         |          3695 |
    'relationship_c', #                   |            18 |
    'business_sector_c', #                |           101 |
    'private_sector_c', #                 |            14 |
    'public_sector_c', #                  |            13 |
    'notes_c', #                          |           889 |
    'contract_type_c', #                  |          2045 |
    'company_region_c', #                 |           688 |
    'other_email_primary_c', #            |            21 |
    'europe_c', #                         |          2559 |
    'company_street_other_c', #           |            17 |
    'company_street_other_2_c', #         |            15 |
    'company_street_other_3_c', #         |            52 |
    'company_city_other_c', #             |            18 |
    'company_post_code_other_c', #        |            17 |
    'shenley_holdings_company_c', #       |          1501 |
    'account_manager_c', #                |           148 |
    'business_development_manager_c', #   |           407 |
    'initial_source_of_referral_c', #     |          1367 |
    'account_manager_2_c', #              |          1853 |
    'business_development_manager_2_c', # |          1774 |
    'contract_end_date_c', #              |            10 |
    'partner_c', #                        |            27 |
    'introducer_c', #                     |             1 |
    'partner_contract_signed_c', #        |             4 |
    'introducer_contract_signed_c', #     |             1 |
    'partnership_terms_c', #              |            45 |
    'introducer_terms_c', #               |             1 |
    'marketing_campaigns_c', #            |          2705 |
    'client_of_c', #                      |            56 |
    'marketing_events_c', #               |          1917 |
    'responsive_to_marketing_c', #        |            15 |
    'media_2_c', #                        |          2586 |
    'elite_customer_c', #                 |           114 |
    'public_sector_new_c', #              |          2422 |
    'private_sector_new_c', #             |           965 |
    'specialism_c', #                     |          1729 |
    'board_private_c', #                  |          1985 |
    'board_public_c', #                   |          1985 |
    'specialism_senior_c', #              |           888 |
    'specialism_middle_c', #              |           377 |
    'title_quaternary_c', #               |            35 |
    'first_name_quaternary_c', #          |           222 |
    'last_name_quaternary_c', #           |           221 |
    'departmentquaternary_c', #           |            42 |
    'email_quaternary_c', #               |           191 |
    'phone_quaternary_c', #               |           178 |
    'ext_quaternary_c', #                 |             4 |
    'mobile_phone_quaternary_c', #        |            27 |
    'contact_id1_c', #                    |            17 |
    'account_id1_c', #                    |            89 |
    'introduced_c', #                     |            70 |
    'specialism_quatenary_c', #           |           199 |
    'job_title_quatenary_c', #            |           167 |
    'added_c', #                          |          2511 |
    'management_level_c', #               |          1169 |
    'management_level_secondary_c', #     |           556 |
    'management_level_tertiary_c', #      |           275 |
    'management_level_quenternary_c', #   |           164 |
    'account_id2_c', #                    |            27 |
    'role_type_c', #                      |           633 |
    'role_type_secondary_c', #            |           127 |
    'role_type_tertiary_c', #             |            58 |
    'role_type_quarternary_c', #          |            35 |
    'marketing_campaigns_primary_c', #    |          1865 |
    'marketing_campaigns_secondary_c', #  |            37 |
    'marketing_campaigns_tertiary_c', #   |            14 |
    'marketing_campaigns_quarternar_c', # |             5 |
    'initial_source_of_referral_p_c', #   |           616 |
    'initial_source_of_referral_t_c', #   |           179 |
    'initial_source_of_referral_q_c', #   |           153 |
    'initial_source_of_referral_s_c', #   |           368 |
    'marketing_events_primary_c', #       |          1743 |
    'marketing_events_secondary_c', #     |          1729 |
    'marketing_events_tertiary_c', #      |          1729 |
    'marketing_events_quarternary_c', #   |          1720 |
    'shenley_holdings_company_new_c', #   |          3145 |
    'hcd_registered_c', #                 |             1 |
    'customer_personal_info_c', #         |            15 |
    'contributor_primary_c', #            |             7 |
    'contributor_secondary_c', #          |             1 |
    'contributor_tertiary_c', #           |             1 |
    'contributor_quarternary_c', #        |             1 |
    'pa_first_name_primary_c', #          |           145 |
    'pa_last_name_primary_c', #           |           136 |
    'pa_phone_primary_c', #               |            69 |
    'pa_email_primary_c', #               |           125 |
    'pa_first_name_secondary_c', #        |            78 |
    'pa_last_name_secondary_c', #         |            72 |
    'pa_email_secondary_c', #             |            67 |
    'pa_phone_secondary_c', #             |            31 |
    'contributor_type_c', #               |             1 |
    'contributor_type_secondary_c', #     |             2 |
    'contritbutor_type_quartenary_c', #   |             2 |
    'finance_first_name_c', #             |            15 |
    'finance_last_name_c', #              |            12 |
    'finance_email_c', #                  |            20 |
    'finance_phone_c', #                  |            17 |
    'contact_type_c', #                   |             1 |
    'lead_generator_c', #                 |           595 |
    'account_id3_c', #                    |             8 |
    'first_conversion_process_c', #       |            53 |
    'network_c', #                        |           845 |
    'ae_services_c', #                    |          1170 |
    'ae_area_c', #                        |          1170 |
    'previously_lindsay_c', #             |            68 |
    'rtw_organisation_type_c', #          |           136 |
    'sales_funnel_c', #                   |            94 |
    )
             }
        }

    def table_contact(self):
        t1 = merge(DataFrame(self.get_data('contacts')),
                   DataFrame(self.get_data('contacts_cstm')),
                   left_index='id',
                   right_index='id_c'
        )

        t2 = self.merge_table_email(t1)
        #t2 = t2[:10] # for debug
        return t2

    def get_mapping_contact(self):
        return {
            'name': self.TABLE_CONTACT,
             'model' : 'res.partner',
            'table': self.table_contact,
             'dependencies' : [self.TABLE_USER],
             'map' :  {
                'id': xml_id(self.TABLE_CONTACT, 'id'),
                 'name': concat('first_name', 'last_name'),
                'create_date': 'date_entered',
                'write_date': 'date_modified',
                'active': lambda record: not record['deleted'],
                 'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),

                'phone':first('phone_home', 'phone_work', 'phone_other', 'home_telephone_c', 'business_telephone_c'),
                'mobile':first('phone_mobile', 'personal_mobile_phone_c'),
                'email':first('email_address', 'personal_email_c', 'business_email_c', 'other_email_c', 'email_c', 'email_2_c'), 

                'fax': first('phone_fax', 'company_fax_c'),
                 'customer': const('0'),
                 'supplier': const('1'),
                 'comment': ppconcat('description', 'birthdate',



#contacts
#'id',#                               | char(36)         |          3957 |
#'date_entered',#                     | datetime         |          3957 |
#'date_modified',#                    | datetime         |          3957 |
#'modified_user_id',#                 | char(36)         |          3957 |
#'created_by',#                       | char(36)         |          3957 |
#'description',#                      | text             |           644 |
#'deleted',#                          | tinyint(1)       |          2843 |
#'assigned_user_id',#                 | char(36)         |          3577 |
#'team_id',#                          | char(36)         |           968 |
#'first_name',#                       | varchar(100)     |          3231 |
#'last_name',#                        | varchar(100)     |          3948 |
'title',#                            | varchar(100)     |           113 |
'department',#                       | varchar(255)     |            32 |
'phone_home',#                       | varchar(25)      |           107 |
'phone_mobile',#                     | varchar(25)      |           161 |
'phone_work',#                       | varchar(25)      |             1 |
'phone_other',#                      | varchar(25)      |             1 |
'phone_fax',#                        | varchar(25)      |            24 |
'birthdate',#                        | date             |            16 |
#contacts_cstm
#'id_c',#                             | char(36)         |          3957 |
'post_nominal_titles_c',#            | varchar(25)      |            30 |
'personal_email_c',#                 | varchar(30)      |            40 |
'business_email_c',#                 | varchar(30)      |            88 |
'other_email_c',#                    | varchar(30)      |             3 |
'home_telephone_c',#                 | varchar(25)      |            32 |
'business_telephone_c',#             | varchar(25)      |            64 |
'personal_mobile_phone_c',#          | varchar(25)      |            92 |
'personal_address_c',#               | varchar(100)     |            44 |
'business_address_c',#               | varchar(100)     |            71 |
'company_c',#                        | varchar(50)      |            92 |
'website_c',#                        | varchar(60)      |          2157 |
'job_title_c',#                      | varchar(60)      |           849 |
'contract_signed_c',#                | tinyint(1)       |             6 |
'case_history_c',#                   | varchar(25)      |            28 |
'daily_rate_c',#                     | varchar(25)      |            29 |
'category_1_c',#                     | varchar(100)     |          3957 |
'category_2_c',#                     | varchar(100)     |          3957 |
'category_3_c',#                     | varchar(100)     |          3957 |
'category_4_c',#                     | varchar(100)     |          3957 |
'category_5_c',#                     | varchar(100)     |          3957 |
'group_company_c',#                  | varchar(100)     |            88 |
'personal_telephone_c',#             | varchar(25)      |            43 |
'valid_insurance_c',#                | varchar(100)     |           971 |
'category_6_c',#                     | varchar(100)     |          3957 |
'referred_business_c',#              | varchar(50)      |             3 |
'vetted_c',#                         | text             |          3039 |
'categories_c',#                     | varchar(255)     |            55 |
'notes_2_c',#                        | varchar(255)     |             2 |
'test_notes_c',#                     | text             |            75 |
'consultant_notes_c',#               | text             |             3 |
'report_writing_skill_c',#           | varchar(100)     |          3957 |
'status_c',#                         | varchar(100)     |          2560 |
'role_c',#                           | text             |           532 |
'consultant_type_c',#                | text             |          1600 |
'title_c',#                          | varchar(100)     |          2884 |
'preferred_contact_c',#              | text             |            92 |
'street_c',#                         | varchar(50)      |           795 |
'street_2_c',#                       | varchar(50)      |           282 |
'street_3_c',#                       | varchar(50)      |           140 |
'city_c',#                           | varchar(30)      |           600 |
'post_code_c',#                      | varchar(25)      |           561 |
'county_c',#                         | varchar(100)     |           971 |
'region_c',#                         | varchar(100)     |          3529 |
'home_phone_c',#                     | varchar(50)      |           620 |
'mobile_phone_c',#                   | varchar(50)      |           993 |
'other_phone_c',#                    | varchar(50)      |            20 |
'email_c',#                          | varchar(150)     |           958 |
'email_2_c',#                        | varchar(100)     |           324 |
'company_status_c',#                 | varchar(100)     |          1052 |
'company_street_c',#                 | varchar(50)      |           915 |
'company_street_2_c',#               | varchar(50)      |           159 |
'company_street_3_c',#               | varchar(50)      |            76 |
'company_city_c',#                   | varchar(50)      |           214 |
'company_post_code_c',#              | varchar(25)      |           234 |
'company_phone_c',#                  | varchar(50)      |           267 |
'company_mobile_phone_c',#           | varchar(50)      |            43 |
'company_fax_c',#                    | varchar(25)      |            97 |
'company_phone_other_c',#            | varchar(50)      |            26 |
'day_c',#                            | varchar(100)     |          3957 |
'month_c',#                          | varchar(100)     |          3957 |
'year_c',#                           | varchar(100)     |           971 |
'gender_c',#                         | varchar(100)     |          1676 |
'investigator_c',#                   | text             |           158 |
'mediator_c',#                       | text             |            76 |
'known_as_c',#                       | varchar(30)      |            16 |
'country_c',#                        | varchar(100)     |           971 |
'england_c',#                        | varchar(100)     |          1749 |
'scotland_c',#                       | varchar(100)     |           995 |
'wales_c',#                          | varchar(100)     |           982 |
'northern_ireland_c',#               | varchar(100)     |          1002 |
'east_midlands_c',#                  | varchar(100)     |           990 |
'east_of_england_c',#                | varchar(100)     |          1009 |
'north_east_england_c',#             | varchar(100)     |           975 |
'north_west_england_c',#             | varchar(100)     |           981 |
'south_east_england_c',#             | varchar(100)     |          1086 |
'south_west_england_c',#             | varchar(100)     |           996 |
'west_midlands_c',#                  | varchar(100)     |           987 |
'registered_disabled_c',#            | tinyint(1)       |             1 |
'nationality_c',#                    | varchar(100)     |          3957 |
'ethnicity_c',#                      | varchar(100)     |          1074 |
'white_c',#                          | varchar(100)     |          3957 |
'asian_or_asian_british_c',#         | varchar(100)     |           971 |
'chinese_and_other_ethnic_group_c',# | varchar(100)     |          3957 |
'black_or_black_british_c',#         | varchar(100)     |           971 |
'first_language_c',#                 | varchar(100)     |          1998 |
'other_languages_c',#                | text             |            28 |
'full_driving_licence_held_c',#      | tinyint(1)       |            86 |
'willing_to_travel_c',#              | varchar(100)     |          1072 |
'general_hr_c',#                     | text             |           129 |
'conflict_dispute_resolutions_c',#   | text             |            22 |
'systems_c',#                        | text             |             2 |
'performance_management_c',#         | text             |            49 |
'wellbeing_and_absenteeism_c',#      | text             |            37 |
'pay_c',#                            | text             |            18 |
'benefits_c',#                       | text             |           670 |
'financial_c',#                      | text             |             4 |
'strategic_c',#                      | text             |            15 |
'diversity_and_equality_c',#         | text             |           100 |
'career_and_retention_c',#           | text             |            72 |
'recruitment_and_assessment_c',#     | text             |            25 |
'development_c',#                    | text             |            13 |
'compliance_and_legal_c',#           | text             |            12 |
'finance_c',#                        | text             |             1 |
'notes_c',#                          | text             |            95 |
'specialism_c',#                     | text             |           389 |
'private_sector_c',#                 | text             |           140 |
'consultant_type_other_c',#          | text             |            50 |
'yorkshire_and_humber_c',#           | varchar(100)     |           979 |
'public_sector_c',#                  | text             |           360 |
'voluntary_sector_c',#               | text             |             3 |
'status_live_c',#                    | text             |          1384 |
'trainer_type_c',#                   | text             |            90 |
'independent_consultant_c',#         | tinyint(1)       |            49 |
'company_name_c',#                   | varchar(60)      |           918 |
'company_email_c',#                  | varchar(40)      |            43 |
'genral_hr_capabilities_c',#         | text             |             3 |
'systems_capabilities_c',#           | text             |             1 |
'performance_management_capabil_c',# | text             |            22 |
'conflict_dispute_resolutions_1_c',# | text             |            42 |
'wellbeing_and_absenteeism2_c',#     | text             |            14 |
'financial1_c',#                     | text             |             1 |
'strategic1_c',#                     | text             |            14 |
'diversity_and_equality1_c',#        | text             |            17 |
'recruitment_and_assessment1_c',#    | text             |             2 |
'development_1_c',#                  | text             |            18 |
'compliance_and_legal1_c',#          | text             |             7 |
'finance1_c',#                       | text             |             2 |
'disabilities_c',#                   | text             |          1291 |
'cpd_c',#                            | text             |           461 |
'qualifications_accreditations_c',#  | text             |           131 |
'psychometric_specialism_c',#        | text             |            13 |
'all_all_c',#                        | tinyint(1)       |            49 |
'religion_c',#                       | varchar(100)     |            46 |
'original_contract_signed_c',#       | varchar(100)     |            42 |
'new_contract_signed_c',#            | varchar(100)     |             9 |
'contract_issued_c',#                | date             |             1 |
'history_c',#                        | text             |             4 |
'minumum_daily_rate_c',#             | varchar(100)     |          1013 |
'unsubscribe_c',#                    | tinyint(1)       |             7 |
'title_2_c',#                        | varchar(100)     |           256 |
'company_1_c',#                      | tinyint(1)       |            26 |
'languages_c',#                      | tinyint(1)       |            27 |
'continent_c',#                      | varchar(100)     |          2693 |
'europe_c',#                         | varchar(100)     |          2693 |
'prg_email_issued_c',#               | varchar(100)     |             8 |
'email_address_permanent_c',#        | varchar(100)     |             7 |
'prg_email_c',#                      | varchar(50)      |            23 |
'prg_business_cards_issued_c',#      | varchar(100)     |             5 |
'status_new_c',#                     | varchar(100)     |           556 |
'status_new1_c',#                    | varchar(100)     |           658 |
'status_live_new_c',#                | varchar(100)     |           310 |
'wellbeing_c',#                      | text             |           687 |
'wellbeing_capabilities_c',#         | text             |             4 |
'united_states_c',#                  | varchar(100)     |          3100 |
'united_states_2_c',#                | varchar(100)     |             3 |
'specialist_c',#                     | tinyint(1)       |             4 |
'ambassador_c',#                     | tinyint(1)       |             4 |
'added_as_candidate_c',#             | date             |           851 |
'went_live_c',#                      | date             |            12 |
'specialist_area_c',#                | varchar(100)     |             6 |
'internal_colleague_c',#             | tinyint(1)       |             5 |
'amabassador_activity_c',#           | text             |           459 |
'specialist_activity_c',#            | text             |           525 |
'partner_c',#                        | tinyint(1)       |             1 |
'introducer_c',#                     | tinyint(1)       |             1 |
'partnership_terms_c',#              | text             |             4 |
'introducer_terms_c',#               | text             |             3 |
'marketing_campaigns_c',#            | text             |           716 |
'marketing_events_c',#               | text             |             4 |
#'contact_id1_c',#                    | char(36)         |            12 |
#'account_id1_c',#                    | char(36)         |             1 |
'introduced_c',#                     | tinyint(1)       |             9 |
'test_c',#                           | varchar(100)     |           100 |
#'contact_id2_c',#                    | char(36)         |             2 |
'shenley_holdings_company_c',#       | text             |          1117 |
'hcd_registered_c',#                 | tinyint(1)       |           270 |
'contributor_type_c',#               | text             |           430 |
'contributor_c',#                    | tinyint(1)       |           122 |
'afp_member_c',#                     | text             |           324 |
'contact_type_c',#                   | text             |          1043 |
'brief_summary_c',#                  | text             |           220 |
'primary_relationship_holder_c',#    | varchar(100)     |           189 |
'devision_c',#                       | varchar(100)     |           165 |
'management_level_c',#               | varchar(100)     |            57 |
'role_type_c',#                      | varchar(100)     |            44 |
'source_of_referral_c',#             | varchar(100)     |             5 |
'skill_set_c',#                      | text             |           302 |
'other_c',#                          | text             |            49 |
#'account_id2_c',#                    | char(36)         |             3 |
'cjsm_email_address_c',#             | varchar(50)      |             5 |
'cjsm_user_name_c',#                 | varchar(50)      |             5 |
'prl_training_required_c',#          | tinyint(1)       |            35 |
'network_c',#                        | text             |             5 |
'training_experience_c',#            | text             |             2 |



                                    )
             }
        }
    def table_case(self):
        t1 = merge(DataFrame(self.get_data('cases')),
                   DataFrame(self.get_data('cases_cstm')),
                   left_index='id',
                   right_index='id_c'
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
             'model' : 'project.task',
            'table': self.table_case,
             'dependencies' : [
                 self.TABLE_USER,
                 self.TABLE_ACCOUNT,
                 self.TABLE_CONTACT,
                 #self.TABLE_LEAD
             ],
             'map' : {
                'id': xml_id(self.TABLE_CASE, 'id'),
                 'name': concat('case_number','case_number_c', 'name', delimiter='-'),
                 'create_date': 'date_entered',
                'active': lambda record: not record['deleted'],
                 'user_id/id': xml_id(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/id': xml_id(self.TABLE_ACCOUNT, 'account_id'),
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
                    }

    def table_filter_modules(self, t, field_name='bean_module'):
        newt = t[(t[field_name] == 'Accounts')|
                (t[field_name] == 'Cases')|
                (t[field_name] == 'Contacts')|
                (t[field_name] == 'Emails')
                ]
        return newt

    def table_email(self):
        t1 = merge(DataFrame(self.get_data('emails')),
                   DataFrame(self.get_data('emails_text')),
                   left_index='id',
                   right_index='email_id'
        )
        t2 = merge(t1,
                   DataFrame(self.get_data('emails_beans')),
                   left_index='id',
                   right_index='email_id',
                   suffixes = ('', '_emails_beans')
        )
        t3 = self.table_filter_modules(t2)
        #t3 = t3[:100] # for debug
        return t3

    map_to_model = {
        'Accounts': 'res.partner',
        'Cases': 'project.task',
        'Contacts': 'res.partner',
        'Prospects': 'TODO',
        'Emails': 'mail.message',
    }
    map_to_table = {
        'Accounts': TABLE_ACCOUNT,
        'Cases': TABLE_CASE,
        'Contacts': TABLE_CONTACT,
        'Prospects': 'TODO',
        'Emails': TABLE_EMAIL,
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
             'model' : 'mail.message',
            'table': self.table_email,
            'dependencies' : [
                self.TABLE_USER,
                self.TABLE_ACCOUNT,
                self.TABLE_CONTACT,
                #self.TABLE_LEAD,
                #self.TABLE_OPPORTUNITY,
                #self.TABLE_MEETING,
                #self.TABLE_CALL
            ],
             'map' : {
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
                    }

    def table_note(self):
        t = merge(DataFrame(self.get_data('notes')),
                   DataFrame(self.get_data('tracker')),
                   left_index='id',
                   right_index='item_id'
        )
        t = self.table_filter_modules(t, 'module_name')

        t = t.dropna(subset=['filename', 'parent_id'], how='any')
        t = t[:10] # for debug
        return t


    def get_mapping_note(self):
        return {
            'name': self.TABLE_NOTE,
            'table': self.table_note,
            'model': 'ir.attachment',
            'dependencies' : [self.TABLE_USER,
                              self.TABLE_ACCOUNT,
                              self.TABLE_CONTACT,
                              #self.TABLE_LEAD,
                              #self.TABLE_OPPORTUNITY,
                              #self.TABLE_MEETING,
                              #self.TABLE_CALL,
                              self.TABLE_EMAIL,
                          ],
            'map': {
                'id': xml_id(self.TABLE_NOTE, 'id'),
                'name':'filename',
                'res_model': map_val('parent_type', self.map_to_model),
                'res_id': res_id(map_val('parent_type', self.map_to_table), 'parent_id'),
                'store_fname': 'filename',
                'type':const('binary'),
                'description': 'description',  # is it used?
                'create_date': 'date_entered',
                'create_uid/id': xml_id(self.TABLE_USER, 'create_by'),
                'company_id/id': const('base.main_company'),
            }
        }
    def get_mapping_history_attachment(self):
        # is not used
        res.append({
            'name': self.TABLE_HISTORY_ATTACHMNET,
             'model' : 'ir.attachment',
             'dependencies' : [self.TABLE_USER, self.TABLE_ACCOUNT, self.TABLE_CONTACT, self.TABLE_LEAD, self.TABLE_OPPORTUNITY, self.TABLE_MEETING, self.TABLE_CALL, self.TABLE_EMAIL],
             'hook' : import_history,
             'map' : {
                 'name':'name',
                 'user_id/id': ref(self.TABLE_USER, 'created_by'),
                 'description': ppconcat('description', 'description_html'),
                 'res_id': 'res_id',
                 'res_model': 'model',
                 'partner_id/.id' : 'partner_id/.id',
                 'datas' : 'datas',
                 'datas_fname' : 'datas_fname'
             }
                    })
    def get_mapping_bug():
        return {
            'name': self.TABLE_BUG,
             'model' : 'project.issue',
             'dependencies' : [self.TABLE_USER],
             'map' : {
                 'name': concat('bug_number', 'name', delimiter='-'),
                 'project_id/id': call(get_bug_project_id, 'sugarcrm_bugs'),
                 'categ_id/id': call(get_category, 'project.issue', value('type')),
                 'description': ppconcat('description', 'source', 'resolution', 'work_log', 'found_in_release', 'release_name', 'fixed_in_release_name', 'fixed_in_release'),
                 'priority': get_project_issue_priority,
                 'state': map_val('status', project_issue_state),
                 'assigned_to/id' : ref(self.TABLE_USER, 'assigned_user_id'),
             }
            }
    def get_mapping_project(self):
        # is not used
        return {
            'name': self.TABLE_PROJECT,
             'model' : 'project.project',
             'dependencies' : [self.TABLE_CONTACT, self.TABLE_ACCOUNT, self.TABLE_USER],
             'hook' : import_project,
             'map' : {
                 'name': 'name',
                 'date_start': 'estimated_start_date',
                 'date': 'estimated_end_date',
                 'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                 'partner_id/.id': 'partner_id/.id',
                 'contact_id/.id': 'contact_id/.id',
                 'state': map_val('status', project_state)
             }
            }
    def get_mapping_project_task(self):
        # is not used
        return {
            'name': self.TABLE_PROJECT_TASK,
             'model' : 'project.task',
             'dependencies' : [self.TABLE_USER, self.TABLE_PROJECT],
             'map' : {
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
            }
    def get_mapping_task(self):
        # is not used
        return {
            'name': self.TABLE_TASK,
             'model' : 'crm.meeting',
             'dependencies' : [self.TABLE_CONTACT, self.TABLE_ACCOUNT, self.TABLE_USER],
             'hook' : import_task,
             'map' : {
                 'name': 'name',
                 'date': 'date',
                 'date_deadline': 'date_deadline',
                 'user_id/id': ref(self.TABLE_USER, 'assigned_user_id'),
                 'categ_id/id': call(get_category, 'crm.meeting', const('Tasks')),
                 'partner_id/id': related_ref(self.TABLE_ACCOUNT),
                 'partner_address_id/id': ref(self.TABLE_CONTACT,'contact_id'),
                 'state': map_val('status', task_state)
             }
            }
    def get_mapping_call(self):
        # is not used
        return {
            'name': self.TABLE_CALL,
             'model' : 'crm.phonecall',
             'dependencies' : [self.TABLE_ACCOUNT, self.TABLE_CONTACT, self.TABLE_OPPORTUNITY, self.TABLE_LEAD],
             'map' : {
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
            }
    def get_mapping_meeting(self):
        # is not used
        return {
            'name': self.TABLE_MEETING,
             'model' : 'crm.meeting',
             'dependencies' : [self.TABLE_CONTACT, self.TABLE_OPPORTUNITY, self.TABLE_LEAD, self.TABLE_TASK],
             'hook': import_meeting,
             'map' : {
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
            }
    def get_mapping_opportunity(self):
        # is not used
        return {
            'name': self.TABLE_OPPORTUNITY,
             'model' : 'crm.lead',
             'dependencies' : [self.TABLE_USER, self.TABLE_ACCOUNT, self.TABLE_CONTACT,self.TABLE_COMPAIGN],
             'hook' : import_opp,
             'map' :  {
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
            }
    def get_mapping_compaign(self):
        # is not used
        return {
            'name': self.TABLE_COMPAIGN,
             'model' : 'crm.case.resource.type',
             'map' : {
                 'name': 'name',
             }
            }
    def get_mapping_employee(self):
        # is not used
        return {
            'name': self.TABLE_EMPLOYEE,
             'model' : 'hr.employee',
             'dependencies' : [self.TABLE_USER],
             'map' : {
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
            }
