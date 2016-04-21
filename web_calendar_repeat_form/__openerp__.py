{
    'name' : 'Fill calendar view popup form automatically with previous data',
    'description': '',
    'description': """
To activate feature in calendar view xml defenition use the following attribute value:

<calendar quick_create_instance="web_calendar_repeat_form.QuickCreateRepeated" >
</calendar>
""",
    'version' : '0.1',
    'author' : 'IT-Projects LLC, Veronika Kotovich',
    'license': 'GPL-3',
    'website' : 'https://twitter.com/vkotovi4',
    'category' : 'Web',
    'depends' : ['web_calendar'],
    'data': ['views.xml'],
    'installable': True
}
