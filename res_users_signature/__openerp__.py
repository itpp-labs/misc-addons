{
    'name' : 'Signature templates for user emails',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Sale',
    'website' : 'https://yelizariev.github.io',
    'description': """
Allows create signature templates for users. For example,

    ---

    <p>${user.name}, ${user.function} of ${user.partner_id.company_id.name}</p>

    <p>${user.phone}, 

    % if user.mobile

    ${user.mobile}, 

    % endif

    ${user.email}</p>

    <p><img src="data:image/png;base64,${user.company_id.logo_web}"/></p>

Will be converted to 

    ---

    <p>Bob, sale manager of You Company</p>

    <p>+123456789, sales@example.com</p>

    <p><img src="data:image/png;base64,ABCDE....12345="/></p>

Tested on 8.0 ab7b5d7732a7c222a0aea45bd173742acd47242d
    """,
    'depends' : ['base', 'hr'],
    'data':[
        'res_users_signature_views.xml',
        'security/res_users_signature_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
