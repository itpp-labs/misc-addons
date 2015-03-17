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

Further information and discussion: https://yelizariev.github.io/odoo/module/2015/03/17/email-signature-template.html
