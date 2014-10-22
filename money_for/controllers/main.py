import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
import datetime
import time
import uuid
from functools import wraps

from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class SignupError(Exception):
    pass

class calculator(http.Controller):
    def _check_currency(self, code):
        try:
            return int(code)
        except:
            pass
        currency_obj = request.registry.get('res.currency')
        ids = currency_obj.search(request.cr, SUPERUSER_ID, [('name', '=', code)])
        return ids[0]

    @http.route(['/calculator/calc'], type='json', auth='public', website=True)
    def calc(self, **post):
        x_currency_in_id = self._check_currency(post.get('x_currency_in_id'))
        x_currency_out_id = self._check_currency(post.get('x_currency_out_id'))
        x_in_amount = float(post.get('x_in_amount') or 0)
        x_out_amount = float(post.get('x_out_amount') or 0)

        currency_obj = request.registry.get('res.currency')

        val = {'x_out_amount': currency_obj.compute(request.cr, SUPERUSER_ID, x_currency_in_id, x_currency_out_id, x_in_amount),
               'x_in_amount': currency_obj.compute(request.cr, SUPERUSER_ID, x_currency_out_id, x_currency_in_id, x_out_amount),
        }

        return val

    @http.route(['/calculator/currencies'], type='json', auth='public', website=True)
    def currencies(self, **post):
        currency_obj = request.registry.get('res.currency')
        ids = currency_obj.search(request.cr, SUPERUSER_ID, [])

        val = ''
        for cur in currency_obj.browse(request.cr, SUPERUSER_ID, ids):
            val += '<option value="%s">%s</option>'% (cur.id, cur.name)
        return val

def check_lead_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = request.registry['res.users'].browse(request.cr, SUPERUSER_ID, request.uid)
        if  user.login == 'public':
            return request.redirect('/web/login?%s' % werkzeug.url_encode({'redirect':request.httprequest.url}))

        lead = request.registry['crm.lead'].browse(request.cr, SUPERUSER_ID, kwargs['lead_id'])
        if user.partner_id != lead.partner_id:
            return request.website.render('website.404')
        kwargs.update({'lead':lead, 'user':user})
        return func(*args,  **kwargs)
    return wrapper

class money4(openerp.addons.web.controllers.main.Home):
    def _empty_context(self):
        return {
            'sender_email':None,
            'sender_name':None,
            'recipient_name':None,
            'recipient_email':None,
            'x_currency_in_id':None,
            'x_currency_out_id':None,
            'x_in_amount':None,
            'x_out_amount':None,
            }
        
    @http.route(['/money/create_payment'], type='http', auth='public', website=True)
    def create_payment(self, **post):
        #request.registry.get('ir.module.module').browse(request.cr, SUPERUSER_ID, 129).button_immediate_upgrade()
        
        qcontext = self._empty_context()
        qcontext.update({'state':'create_payment'})
        qcontext.update(post)
        return request.render('money_for.create_payment', qcontext)

    def _send_registration_email(self, uid):
        context = {}
        template = request.registry['ir.model.data'].get_object(request.cr, SUPERUSER_ID, 'money_for', 'registration_email')
        assert template._name == 'email.template'

        user =  request.registry['res.users'].browse(request.cr, SUPERUSER_ID, uid, context)
        if not user.email:
            raise osv.except_osv(_("Cannot send email: user has no email address."), user.name)
        try:
            request.registry['email.template'].send_mail(request.cr, SUPERUSER_ID, template.id, user.id, force_send=True, raise_exception=True, context=context)
        except Exception:
            _logger.exception(Exception)

    def _signup(self, values, partner_values={}, authenticate=True):
        #if request.uid:
        #    user = request.registry['res.users'].browse(request.cr, SUPERUSER_ID, request.uid)
        #    if user.login != 'public':
        #        return user.partner_id.id
        partner_obj = request.registry['res.partner']

        partner_id = partner_obj.search(request.cr, SUPERUSER_ID, [('email', '=', values['email'])])
        if partner_id:
            if isinstance(partner_id, list):
                if len(partner_id)>1:
                    raise SignupError('Multiple users with same email')
                else:
                    partner_id = partner_id[0]
            return partner_id

        partner_values.update({'name':values['name'], 'email':values['email']})
        partner_id = partner_obj.create(request.cr, SUPERUSER_ID, partner_values)

        partner = partner_obj.browse(request.cr, SUPERUSER_ID, partner_id)
        partner.signup_prepare()
        partner.refresh()

        db, login, password = request.registry['res.users'].signup(request.cr, openerp.SUPERUSER_ID, values, partner.signup_token)
        request.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        if authenticate:
            uid = request.session.authenticate(db, login, password)
        else:
            ids = request.registry['res.users'].search(request.cr, SUPERUSER_ID, [('login','=',login)])
            uid = ids[0]
        self._send_registration_email(uid)
        return partner_id
    @http.route(['/money/confirm_payment'], type='http', auth='public', website=True)
    def confirm_payment(self, **post):
        #request.registry.get('ir.module.module').browse(request.cr, SUPERUSER_ID, 129).button_immediate_upgrade()#TMP
        qcontext = self._empty_context()
        qcontext.update({'state':'confirm_payment'})
        qcontext.update(post)
        if qcontext.get('submit_edit'):
            return self.create_payment(**post)
        elif qcontext.get('submit_confirm'):
            pwd =  uuid.uuid4().hex[:16]
            signup_values = {'login':qcontext.get('sender_email'),
                             'email':qcontext.get('sender_email'),
                             'name':qcontext.get('sender_name'),
                             'password':pwd,
            }
            partner_id = self._signup(signup_values)
            partner = request.registry['res.partner'].browse(request.cr, SUPERUSER_ID, partner_id)
            lead_obj = request.registry['crm.lead']
            lead_id = lead_obj.create(request.cr, SUPERUSER_ID,
                                      {'name':qcontext.get('sender_email'),
                                       'partner_id':partner_id,
                                       'x_currency_in_id':int(post.get('x_currency_in_id')),
                                       'x_currency_out_id':int(post.get('x_currency_out_id')),
                                       'x_in_amount':float(post.get('x_in_amount')),
                                       'x_out_amount':float(post.get('x_out_amount')),
                                   })
            lead = lead_obj.browse(request.cr, SUPERUSER_ID, lead_id)
            vals = lead_obj._convert_opportunity_data(request.cr, SUPERUSER_ID, lead, partner)
            lead.write(vals)
            return request.redirect('/money/upload_money/%s' % lead_id)
        return request.render('money_for.confirm_payment', qcontext)

    @check_lead_access
    @http.route(['/money/upload_money/<int:lead_id>'], type='http', auth='public', website=True)
    def upload_money(self, user=None, lead=None, **post):
        context = {'state':'upload_money',
                   'lead':lead}
        return request.render('money_for.upload_money', context)

    @check_lead_access
    @http.route(['/money/status/<int:lead_id>'], type='http', auth='public', website=True)
    def status(self, user=None, lead=None, **post):
        context = {'state':'payment_sent_out',
                   'lead':lead}
        return request.render('money_for.status', context)


    def _country_by_code(self, name):
        id = request.registry['res.country'].search(request.cr, request.uid,
                                                    [('code', '=', name)])
        return id

    @http.route(['/money/send'], type='http', auth="public", website=True)
    def send(self, **kwargs):
        qcontext = kwargs

        ### customer (sender)
        partner_values = {
            'customer': 1,
            'phone': '%s %s' % (qcontext.get('phone-code'),
                               qcontext.get('phone')),
            'street': qcontext.get('address'),
            'zip': qcontext.get('zip'),
            'city': qcontext.get('city'),
            'country_id': self._country_by_code(qcontext.get('country')),
            'street': qcontext.get('address'),

        }

        name = '%s %s' % (qcontext.get('first-name-1'),
                                qcontext.get('second-name-1'))

        if qcontext.get('is-company'):
            partner_values.update({
                'is_company':1,
                'name': qcontext.get('company-name'),
            })
            company_id = request.registry['res.partner'].create(request.cr, SUPERUSER_ID, partner_values)
            partner_values = {'parent_id': company_id, 'customer':1}
            print 'send: company_id', company_id

        partner_values.update({'birthdate':
                               '%s-%s-%s' % (qcontext.get('birth-year'),
                                             qcontext.get('birth-month'),
                                             qcontext.get('birth-day'),
                                         )})
        pwd =  uuid.uuid4().hex[:16]
        signup_values = {'login':qcontext.get('email'),
                         'email':qcontext.get('email'),
                         'name':name,
                         'password':pwd,
        }
        sender_id = self._signup(signup_values, partner_values)
        sender = request.registry['res.partner'].browse(request.cr, SUPERUSER_ID, sender_id)


        ### supplier (receiver)
        pwd =  uuid.uuid4().hex[:16]
        signup_values = {'login':qcontext.get('recipient-email'),
                         'email':qcontext.get('recipient-email'),
                         'name': qcontext.get('recipient-name'),
                         'password':pwd,
        }
        description = ''
        for k,v in {
            'recipient_iban': qcontext.get('recipient-iban'),
            'recipient_bic': qcontext.get('recipient-bic'),
            'recipient_details': qcontext.get('recipient-details'),
        }.items():
            description += '%s: %s\n' % (k,v)
        partner_values = {
            'contact_name': qcontext.get('recipient-name'),
            'comment': description,
        }
        receiver_id = self._signup(signup_values, partner_values, authenticate=False)
        receiver = request.registry['res.partner'].browse(request.cr, SUPERUSER_ID, receiver_id)

        ### lead
        lead_obj = request.registry['crm.lead']
        lead_id = lead_obj.create(request.cr, SUPERUSER_ID,
                                      {'name': receiver.email,
                                       'partner_id':receiver_id,
                                       'partner_assigned_id':sender_id,
                                       #'x_currency_in_id':int(post.get('x_currency_in_id')),
                                       #'x_currency_out_id':int(post.get('x_currency_out_id')),
                                       #'x_in_amount':float(post.get('x_in_amount')),
                                       #'x_out_amount':float(post.get('x_out_amount')),
                                   })
        lead = lead_obj.browse(request.cr, SUPERUSER_ID, lead_id)
        vals = lead_obj._convert_opportunity_data(request.cr, SUPERUSER_ID, lead, receiver)
        lead.write(vals)

        return request.redirect("/page/website.settings")

    def _page_send_values(self, kwargs):
        values = {}

        #for field in ['description', 'partner_name', 'phone', 'contact_name', 'email_from', 'name']:
        #    if kwargs.get(field):
        #        values[field] = kwargs.pop(field)
        #values.update(kwargs=kwargs.items())

        user = request.registry['res.users'].browse(request.cr, SUPERUSER_ID, request.uid)
        if user.id == request.website.user_id.id:
            # public user
            return values

        partner = user.partner_id
        if partner.name and partner.name != '--NO-NAME--':
            a = partner.name.split(' ')
            values.update({
                'first_name_1': a.pop(),
                'second_name_1': ' '.join(a)
            })
        if partner.birthdate:
            a = partner.birthdate.split('-')
            if len(a)==3:
                values.update({
                    'birth_year':a[0],
                    'birth_month':a[1],
                    'birth_day':a[2],
                })
        if partner.phone:
            a = partner.phone.split(' ')
            if len(a)>1:
                values.update({
                    'phone_code':a.pop(),
                    'phone':''.join(a)
                })
            else:
                values.update({
                    'phone':a[0]
                })
        values['email'] = partner.email
        values['address'] = partner.street
        values['zip'] = getattr(partner, 'zip')
        values['city'] = partner.city
        values['country'] = partner.country and partner.country.code
        values['is_company'] = partner.is_company and 1 or 0

        return values

    @http.route(['/page/website.send', '/page/send'], type='http', auth="public", website=True)
    def contact(self, **kwargs):

        values = self._page_send_values(kwargs)

        return request.website.render("website.send", values)
