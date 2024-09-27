# -*- coding: utf-8 -*-
import json
import itertools
import pytz
import base64
import babel.dates
import werkzeug
import requests
import logging
import string
import odoo
import math
from requests.exceptions import ConnectionError, ConnectTimeout
from io import BytesIO, StringIO
from re import compile
from xml.etree import cElementTree as ET
from pytube import extract
from collections import OrderedDict
import babel.dates
import re
from werkzeug.datastructures import OrderedMultiDict
from werkzeug.exceptions import Forbidden, NotFound
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


from odoo.exceptions import AccessError, UserError
from odoo import http, fields
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request, content_disposition
from odoo.osv import expression
from odoo.tools import html2plaintext
from odoo.tools.image import image_data_uri
from odoo.tools.misc import get_lang
from odoo import http, tools, _
from odoo.modules.module import get_module_resource
# from odoo.addons.web.controllers.main import serialize_exception
from odoo.addons.web.controllers.main import ensure_db, Home as WebHome
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.survey.controllers.main import Survey
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import Binary
from odoo.exceptions import AccessError, UserError
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.http import request

_logger = logging.getLogger(__name__)
PROFILE_TOTAL_POINTS = 56


def bpd_authenticate_cedula(cedula, instance):

    result = {"error": False, "result": False}
    prod_url = "https://api.bpd.com.do/bpd/sb/cedulado/validacioncedula"
    prod_client_id = "7d721e93-056b-41e3-9377-5324bd2c0857"
    prod_client_secret = "aJ8vO7rL0gI5rK2uR8lA5lW5cJ0wB8cU6jV1tV3eB4tR8rD6cQ"
    prod_url_service = "http://10.32.8.133:8010/RestApi/CeduladosQUEUE?cedula="

    test_url = "https://apiqa.bpd.com.do/bpdqa/sb/cedulado/validacioncedula"
    test_client_id = "ea594a74-fe00-4976-9271-8ea02a168c8f"
    test_client_secret = "jK6jO5yM6rR5yP2fQ3pK3pK8dR1tU0uL1sQ0iV7hA8oD5jU4bI"
    test_url_service = "http://10.15.20.188:97/RestApi/CeduladosQUEUE?cedula="

    headers = {
        'X-IBM-Client-Id': False,
        'Content-Type': "application/xml",
        'accept': "application/xml",
        'urlservice':  False,
        'X-IBM-Client-Secret':  False,
        'Cache-Control': "no-cache",
        'Postman-Token': "d5782a0c-5ca2-42ca-99c3-912ee2c44352"
    }

    if instance == 'prod':
        headers.update({
            'X-IBM-Client-Id': prod_client_id,
            'urlservice': prod_url_service,
            'X-IBM-Client-Secret': prod_client_secret,
        })
        api_url = prod_url
    else:
        headers.update({
            'X-IBM-Client-Id': test_client_id,
            'urlservice': test_url_service,
            'X-IBM-Client-Secret': test_client_secret,
        })
        api_url = test_url

    response = False
    payload = """
    <MESSAGE type='RQ'>
        <DATA>
            <CUSTOMER DOCUMENT-NUMBER='%s' DOCUMENT-TYPE='CEDULA'/>
        </DATA>
    </MESSAGE>
    """ % cedula

    try:
        response = requests.request(
            "POST",
            api_url,
            data=payload,
            headers=headers,
            verify=True
        )
    except ConnectionError as e:
        _logger.info("Error validando cedula: %r" % e)
        result.update({
            "error": "Error de conexión al válidar la cédula"
        })

    if response and response.status_code == 200:
        xml_string = response.content.decode('utf-8')
        root = ET.XML(xml_string)
        data_node = root.findall('DATA')
        if len(data_node) == 1:
            data_node_value = data_node[0]
            valid_node = data_node_value.findall('VALID')
            if len(valid_node) == 1:
                valid_node_value = valid_node[0]
                if valid_node_value.text == "TRUE":
                    result['result'] = True
                else:
                    result['error'] = "Número de cédula inválida."
                    result['result'] = False
    elif response and response.status_code != 200:
        result['error'] = "Número de cédula inválida."
        result['result'] = False

    return result


class AuthSignupController(AuthSignupHome):

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and
        reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                partner = request.env['res.partner'].sudo()
                # retrieve the user info (name, login or email) corresponding
                # to a signup token
                token_infos = partner.signup_retrieve_info(qcontext.get(
                    'token'))
                token_infos.update({
                    'vat': partner.vat,
                    'lastname': partner.lastname,
                })
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    @http.route('/web/signup', type='http', auth='public', website=True,
        sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        error_message = ""
        bpd_api_instance = request.env['ir.config_parameter'].sudo(
        ).get_param('bpd.api')
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        valid_identification = True
        login_status = 'valid'
        if kw.get('cedula'):
            cedula = kw.get('cedula').replace('-', '')
            if bpd_api_instance and bpd_api_instance != 'prod' and kw.get(
                    'user_type') == 'adult':
                rstl = bpd_authenticate_cedula(cedula, bpd_api_instance)
                is_valid = rstl.get('result')
                if not is_valid:
                    valid_identification = False
                    login_status = 'invalid'

            # First check this identification doesn't exist
            partner = request.env['res.partner'].sudo().search([
                ('active', '=', True),
                ('vat', '=', cedula),
                ('email', '=', kw.get('login')),
            ])
            if len(partner) > 1 or len(partner) == 1 and partner.email != \
                    kw.get('login'):
                error_message = "Ya existe un usuario registrado con este " \
                                "número de cédula."
        if kw:
            if kw.get('name') and not kw['name'].replace(" ", "").isalpha():
                error_message = '¡Nombre inválido! Por favor, introducir un ' \
                                'nombre válido. Solo se aceptan caracteres.'
            elif kw.get('login') and not tools.single_email_re.match(
                    kw.get('login')):
                error_message = '¡Email inválido! Por favor, introducir una ' \
                                'dirección de correo electrónico válida.'
            elif kw.get('password'):
                pwd_msg = "La contraseña debe tener al entre 8 y 16 " \
                          "caracteres, al menos un dígito, al menos una " \
                          "minúscula, al menos una mayúscula y al menos un " \
                          "caracter no alfanumérico."
                # and not len(kw.get('password')) > 7:
                regex = "^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])\S{8,16}$"
                pattern = compile(regex)
                if not bool(pattern.match(kw.get('password'))):
                    error_message = pwd_msg
            elif kw.get('user_accept_terms') and not kw.get(
                    'user_accept_terms'):
                error_message = 'Por favor asegurese de leer nuestros ' \
                                'términos y condiciones y aceptarlo, lo ' \
                                'encontrara al pie de la página'

        if error_message:
            qcontext.update({
                'error': error_message
            })

        qcontext['last_name'] = kw.get('lastname')

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(kw.get('login')),
                    order=User._get_login_order(), limit=1
                )

                # Update partner values
                if user_sudo:
                    _logger.info("Creando usuario: %r" % kw)
                    _logger.info("Datos usuario: %s | %s" % (
                        user_sudo.partner_id.name, user_sudo.partner_id.lastname
                    ))

                    gender = False
                    if kw.get('gender', False):
                        gender = kw.get('gender')
                        user_sudo.write({
                            'gender': gender,
                            'user_type': kw.get('user_type'),
                            'user_status': valid_identification,

                        })

                    user_sudo.partner_id.write({
                        'vat': kw.get('cedula').replace('-', ''),
                        'lastname': kw.get('lastname'),
                        'gender': gender,
                        'user_type': kw.get('user_type'),
                        'user_status': valid_identification,
                        'login_status': login_status,
                        'country_id': request.env.ref('base.do').id,
                    })

                # Send an account creation confirmation email
                if qcontext.get('token'):
                    mail_template = "mail_template_user_signup_account_created"
                    template = request.env.ref(
                        'elearning_features.%s' % mail_template,
                        raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode(
                                {'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search(
                        [("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _(
                        "Another user is already registered using this email "
                        "address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _(e)

        _logger.info("Context en error: %r" % qcontext)
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext.update({
            'user_is_reseting_password': True,
            'cedula': request.env.user.partner_id.vat,
            'last_name': request.env.user.partner_id.lastname,
            'lastname': request.env.user.partner_id.lastname,
        })

        if not qcontext.get('token') and not qcontext.get(
                'reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if qcontext.get('password'):
            pwd_msg = "La contraseña debe tener al entre 8 y 16 " \
                      "caracteres, al menos un dígito, al menos una " \
                      "minúscula, al menos una mayúscula y al menos un " \
                      "caracter no alfanumérico."

            regex = "^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])\S{8,16}$"
            pattern = compile(regex)
            if not bool(pattern.match(qcontext.get('password'))):
                qcontext['error'] = pwd_msg

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login,
                        request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _(
                        "An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class HomeController(WebHome):

    @http.route(
        '/account/email_confirm', type='http', auth="public", website=True)
    def confirm_email(self, user_id):
        user = request.env['res.users'].sudo().browse(int(user_id))
        return request.render('website.email_validation', {
            'user': user,
            'resend': False,
        })

    @http.route('/account/validate_email', type='http', auth='public',
        website=True)
    def account_validate_email(self, token, user_id, email):
        # Check token
        user = request.env['res.users'].sudo().browse(int(user_id))
        done = user._process_account_validation_token(user.id, token, email)

        if done and user:
            # Update user value
            user.write({
                'is_account_confirmed': True,
            })
            return request.render('website.account_confirm', {})

        return request.redirect('/web')

    @http.route('/account/email/resend', type='http', auth='public',
        website=True)
    def account_email_resend(self, user_id):
        # Reresend emial
        user = request.env['res.users'].sudo().browse(int(user_id))
        user._send_account_validation_email()
        request.session.logout(keep_db=True)
        return request.render('website.email_validation', {
            'user': user,
            'resend': True,
        })

    @http.route()
    def web_login(self, *args, **kw):
        response = super(HomeController, self).web_login(*args, **kw)

        if kw.get('cedula'):
            cedula = kw.get('cedula').replace('-', '')
            # First check this identification doesn't exist
            partners = request.env['res.partner'].sudo().search([
                ('active', '=', True),
                ('vat', '=', cedula),
            ])
            if len(partners) > 1:
                error_msg = "Ya existe un usuario registrado con este " \
                           "número de cédula."
                kw.update({
                    'login_success': False,
                    'error': error_msg,
                    'signup_enabled': True,
                    'reset_password_enabled': True
                })
            else:
                bpd_api_instance = request.env['ir.config_parameter'].sudo(
                ).get_param('bpd.api')
                _logger.info("Validacion cedula comentada")
                if bpd_api_instance and bpd_api_instance == 'prod' and kw.get(
                        'user_type') == 'adult':
                    rstl = bpd_authenticate_cedula(
                        kw.get('cedula'), bpd_api_instance)
                    is_valid = rstl.get('result')
                    if not is_valid:
                        kw.update({
                            'login_success': False,
                            'error': valid_identification.get('error')
                        })

            if kw.get('error'):
                login_response = request.render('auth_signup.login', kw)
                login_response.headers['X-Frame-Options'] = 'DENY'
                request.session.logout(keep_db=True)
                return login_response

        token = request.params.get('token')
        if request.params.get('confirm_password') and request.session.uid \
                and not token:
            # Send confirmation email
            request.env.user._send_account_validation_email()
            request.session.logout(keep_db=True)
            return request.redirect('/account/email_confirm?user_id=%d' %
                                    request.env.user.id)

        # Check account was verified
        user = request.env.user.sudo()
        if user.is_account_confirmed:
            request.session['validation_email_done'] = True
            request.session['validation_email_sent'] = True

        if user.login == kw.get('login') and not user.is_account_confirmed:
            request.session.logout(keep_db=True)
            # response.qcontext['error'] = "No puede iniciar sesión hasta " \
            #                              "confirmar su cuenta."
            kw.update({
                'login_success': False,
                'error': "No puede iniciar sesión hasta confirmar su cuenta.",
                'signup_enabled': True,
                'reset_password_enabled': True
            })
        elif user.login == kw.get('login') and user.is_account_confirmed:
            user.write({
                'website_published': True,
                'karma': 3 if user.karma == 0 else user.karma,
            })
            user.partner_id.write({
                'country_id': request.env.ref('base.do').id,
            })
            request.session['validation_email_done'] = True
            request.session['validation_email_sent'] = True
            redirect_url = kw.get('redirect_url', '/profile/user/%d' % user.id)

            if user.has_group('base.group_portal') and user.profile_percent < 100.0:
                redirect_url = "/profile/edit?url_param=''&user_id=%d" % user.id
                return request.redirect(redirect_url)

            return http.redirect_with_hash(self._login_redirect(user.id, redirect=kw.get('redirect', '')))

        _logger.info("Params: %r" % kw)
        _logger.info("Response: %r" % response)
        response = request.render('web.login', kw)
        _logger.info("Final Response: %r" % response)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class Profile(WebsiteProfile):

    @http.route(['/perfil/usuarios', '/profile/users',
                 '/profile/users/page/<int:page>'], type='http', auth="user",
                website=True)
    def view_all_users_page(self, page=1, **searches):
        if page:
            raise NotFound()

        User = request.env['res.users']
        dom = [('karma', '>', 1), ('website_published', '=', True)]

        # Searches
        search_term = searches.get('search')
        if search_term:
            dom = expression.AND([['|', ('name', 'ilike', search_term),
                                   ('company_id.name', 'ilike', search_term)],
                                  dom])

        user_count = User.sudo().search_count(dom)

        if user_count:
            page_count = math.ceil(user_count / self._users_per_page)
            pager = request.website.pager(
                url="/profile/users",
                total=user_count, page=page,
                step=self._users_per_page,
                scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

            users = User.sudo().search(dom, limit=self._users_per_page,
                                       offset=pager['offset'],
                                       order='karma DESC')
            user_values = self._prepare_all_users_values(users)

            # Get karma position for users (only website_published)
            position_domain = [('karma', '>', 1),
                               ('website_published', '=', True)]
            position_map = self._get_users_karma_position(position_domain,
                                                          users.ids)
            for user in user_values:
                user['position'] = position_map.get(user['id'], 0)

            values = {
                'top3_users': user_values[
                              :3] if not search_term and page == 1 else None,
                'users': user_values[
                         3:] if not search_term and page == 1 else user_values,
                'pager': pager
            }
        else:
            values = {'top3_users': [], 'users': [], 'search': search_term,
                      'pager': dict(page_count=0)}

        return request.render("website_profile.users_page_main", values)

    @http.route(['/user/get_cities'], type='http', auth="public", website=True)
    def get_cities(self, *args, **kw):
        """This route is called when changing city from the user profile"""

        cities = []
        if kw.get('id_state'):
            id_state = int(kw.get('id_state'))
            record = request.env['res.country.city'].search([
                ('state_id', '=', id_state),
            ])

            for city in record:
                cities.append({'name': city.name, 'id': city.id})

        return json.dumps(cities)

    @http.route(['/user/get_towns'], type='http', auth="public", website=True)
    def get_towns(self, *args, **kw):
        """This route is called when changing state from the user profile"""

        towns = []

        if kw.get('id_state'):
            id_state = int(kw.get('id_state'))
            record = request.env['res.country.town'].search([
                ('state_id', '=', id_state),
            ])

            for town in record:
                towns.append({'name': town.name, 'id': town.id})

        return json.dumps(towns)

    @http.route(['/profile/user/update_province'], type='json', auth="public",
                methods=['POST'], website=True, csrf=False)
    def update_province_json(self, city_id):
        """This route is called when changing city from the user profile"""
        city = request.env['rec.country.city'].browse([city_id])
        return {'state_id': city.state_id.id}

    def _profile_edition_preprocess_values(self, user, **kwargs):

        values = super(Profile, self)._profile_edition_preprocess_values(
            user, **kwargs)
        state_id, city = False, False

        if kwargs.get('state', False):
            state_id = int(kwargs.get('state'))
            state = request.env['res.country.state'].browse([state_id])
            city = state.name

        _logger.info("Profile Edit: %r" % kwargs)
        values.update({
            'name': kwargs.get('user_only_name'),
            'user_only_name': kwargs.get('user_only_name'),
            'user_last_name': user.partner_id.lastname,
            'lastname': kwargs.get('user_last_name'),
            'gender': kwargs.get('gender'),
            'user_type': kwargs.get('user_type'),
            'sector': kwargs.get('sector'),
            'birthday': kwargs.get('birthday'),
            'age': kwargs.get('age'),
            'workplace': kwargs.get('workplace'),
            'goals_first': kwargs.get('goals_first'),
            'goals_second': kwargs.get('goals_second'),
            'goals_third': kwargs.get('goals_third'),
            'goals_financial_first': kwargs.get('goals_financial_first'),
            'goals_financial_second': kwargs.get('goals_financial_second'),
            'goals_financial_third': kwargs.get('goals_financial_third'),
            'vat': kwargs.get('vat'),
            'phone': kwargs.get('phone'),
            'mobile': kwargs.get('mobile'),
            'street': kwargs.get('street'),
            'provincia': kwargs.get('provincia'),
            'municipio': kwargs.get('municipio'),
            'distritos_municipales': kwargs.get('distritos_municipales'),
            'country_id': int(kwargs.get('country')) if kwargs.get(
                'country') else request.env.ref('base.DO').id,
            'website': kwargs.get('website', False),
        })
        if kwargs.get('user_last_name'):
            user.partner_id.write({'lastname': kwargs.get('user_last_name')})
        if kwargs.get('mobile'):
            user.partner_id.write({'mobile': kwargs.get('mobile')})
        if kwargs.get('gender'):
            user.partner_id.write({'gender': kwargs.get('gender')})

        return values

    def _prepare_user_values(self, **kwargs):

        values = super(Profile, self)._prepare_user_values(**kwargs)

        countries = request.env['res.country'].sudo().search(
            [('code', '=', 'DO')])
        states, cities, towns = [], [], []
        country_id = request.env['res.country'].search([('code', '=', 'DO')])

        if country_id:
            states = request.env['res.country.state'].search([
                ('country_id', '=', country_id.id)])

        _logger.info("Profile values: %r" % values)
        pup = 0  # pup profile_user_point
        percent = 0
        user = values.get('user') or request.env.user
        lastname_user = False
        phone_user = False
        if user.lastname:
            lastname_user = user.partner_id.lastname
        if user.partner_id.lastname:
            lastname_user = user.partner_id.lastname

        if user.partner_id.phone:
            phone_user = user.partner_id.phone

        if user.partner_id.mobile:
            phone_user = user.partner_id.mobile

        if user:
            if user.name:
                pup += 5
            if lastname_user:
                pup += 5
            if phone_user:
                pup += 3
            if user.birthday:
                pup += 3
            # if user.partner_id.website:
            #     pup += 3
            if user.partner_id.email:
                pup += 5
            if user.partner_id.gender and user.partner_id.gender != "":
                pup += 5
            if user.phone:
                pup += 3
            if user.mobile:
                pup += 3
            if user.sector:
                pup += 3
            if user.provincia:
                pup += 3
            if user.municipio:
                pup += 3
            if user.distritos_municipales:
                pup += 3
            if user.workplace:
                pup += 3
            if user.goals_first:
                pup += 1
            if user.goals_second:
                pup += 1
            if user.goals_third:
                pup += 1
            if user.goals_financial_first:
                pup += 1
            if user.goals_financial_second:
                pup += 1
            if user.goals_financial_third:
                pup += 1
            if user.partner_id.website_description:
                pup += 8

        if pup > 0:
            percent = 100 * float(pup) / float(PROFILE_TOTAL_POINTS)
            if percent > 100.0:
                percent = 100.0

        user.sudo().write({'profile_percent': percent})
        validation_email_done = False
        if user.is_account_confirmed:
            validation_email_done = True
        _logger.info("Profile Update: %r" % kwargs)
        _logger.info("Profile Update gender: %r" % user.gender)
        values.update({
            'user_last_name': user.partner_id.lastname,
            'validation_email_done': validation_email_done,
            'profile_percent': int(percent),
            'profile_percent_class': " center c100 p" + str(int(percent)),
            'gender': user.gender or user.partner_id.gender or False,
            'user_type': user.user_type or user.partner_id.user_type or False,
            'countries': countries,
            'states': states,
            'karma': user.karma,
            'cities': request.env['res.country.city'].search([
                ('state_id', '=', user.partner_id.state_id.id)
            ]),
            'towns': request.env['res.country.town'].search([
                ('state_id', '=', user.partner_id.state_id.id)
            ]),
        })
        return values

    @http.route('/profile/validate_email', type='http', auth='public',
                website=True, sitemap=False)
    def validate_email(self, token, user_id, email, **kwargs):
        done = request.env['res.users'].sudo().browse(
            int(user_id))._process_profile_validation_token(token, email)
        user = request.env.user
        if done or user.is_account_confirmed:
            request.session['validation_email_done'] = True
        url = kwargs.get('redirect_url', '/')
        return request.redirect(url)

    @http.route('/profile/validate_email/close', type='json', auth='public',
                website=True)
    def validate_email_done(self, **kwargs):
        user = request.env.user
        if user.is_account_confirmed:
            request.session['validation_email_done'] = True
        else:
            request.session['validation_email_done'] = False
        return True


class AcademiaControllers(http.Controller):

    @http.route('/cursos/channel/teacher/follow', type='json', auth='public',
                website=True)
    def slide_channel_favorite(self, channel_id, partner_id):
        success = request.env['slide.teacher.follower'].sudo().create({
            'channel_id': int(channel_id),
            'partner_id': int(partner_id),
        })

        if not success:
            return {'error': 'fail'}
        else:
            channel = request.env['slide.channel'].sudo().browse([int(
                channel_id)])
            channel.write({'is_teacher_follower': True})
        return {'success': success}

    @http.route(['/cursos/channel/teacher/unfollow'], type='json',
        auth='public', website=True)
    def slide_channel_unfavorite(self, channel_id, partner_id):
        partner_follower = request.env['slide.teacher.follower'].sudo().search([
            ('channel_id', '=', int(channel_id)),
            ('partner_id', '=', int(partner_id)),
        ])

        if partner_follower:
            partner_follower.unlink()
            channel = request.env['slide.channel'].sudo().browse([int(
                channel_id)])
            channel.write({'is_teacher_follower': False})
            return {'success': 'done'}
        else:
            return {'error': 'fail'}

    @http.route('/docentes', type='http', auth="public", website=True)
    def teachers(self):
        teachers = request.env['res.partner'].sudo().search([
            ('is_teacher', '=', True)
        ])

        return request.render("elearning_features.teachers", {
            'teachers': teachers})

    @http.route('/profile/teacher/<int:user_id>', type='http', auth="public", website=True)
    def teacher_profile(self, user_id):
        user = request.env['res.users'].sudo().browse([user_id])
        slides = request.env['slide.channel'].sudo().search([('teacher_ids','in',user.id)])

        partner_image = False
        if user.partner_id.image_1920:
            partner_image = user.partner_id.image_1920.decode('ascii')

        values = {
            'id': user.id,
            'partner': user.partner_id,
            'image': partner_image,
            'userimage': '/web/image?model=res.users&id=%s&field=image_128' % user.id,
            'name': user.name,
            'function': user.partner_id.function,
            'rank': user.rank_id.name,
            'karma': user.karma,
            'badge_count': len(user.badge_ids),
            'website_published': user.website_published,
            'slides': slides
        }
        return request.render("elearning_features.teacher_profile", {
            'user': values})

    @http.route('/web/centro-de-ayuda', type='http', auth="public", website=True)
    def help_center(self):
        records = request.env['website.help.center'].sudo().search([
            ('active', '=', True)
        ])
        return request.render("elearning_features.centro_de_ayuda", {
            'records': records})

    @http.route('/documentos', type='http', auth="public", website=True)
    def documents(self):
        folder = request.env['documents.folder'].sudo().search([
            ('use_in_website', '=', True),
            ('parent_folder_id', '=', False),
        ])
        documents = request.env['documents.document'].sudo().search([
            ('folder_id', 'in', folder.ids),
        ])
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        values = {
            'content': '%s/documents/content/' % base_url,
            'folders': folder,
            'documents': documents,
        }

        return request.render("elearning_features.documents", values)

    @http.route('/capsulas-educativas', type='http', auth="public", website=True)
    def capsulas_educativas(self):
        folder = request.env['documents.folder'].sudo().search([
            ('use_in_website', '=', True),
            ('use_in_capsule', '=', True),
            ('parent_folder_id', '=', False),
        ])

        values = {
            'folder_name': folder.name,
            'main_video': False,
            'documents': [],
        }
        for doc in folder.document_ids:
            owner = doc.partner_id
            owner_name = owner.name
            if owner.lastname:
                owner_name += " %s" % owner.lastname

            info = {}
            if 'vimeo' in doc.url:
                api_vimeo = "https://vimeo.com/api/oembed.json?url={}".format(
                    doc.url)
                try:
                    data = requests.get(api_vimeo)
                    if data.status_code == 200:
                        data = data.json()
                        src = data.get('html').split(' ')[1]
                        link = src.replace('src="', '').replace('"', '')
                        info = {
                            'id': doc.id,
                            'name': data.get('title'),
                            'author_name': data.get('author_name'),
                            'owner_name': owner_name,
                            'description': data.get('description'),
                            'embed_code': link,
                        }
                except requests.exceptions.ConnectionError as e:
                    pass
            _logger.info("Document info: %r" % info)
            if doc.main_video:
                values['main_video'] = info
            else:
                values['documents'].append(info)
        _logger.info("Capuslas info: %r" % values)
        return request.render("elearning_features.capsulas_educativas", values)

    @http.route('/capsula/<model("documents.document"):document>', type='http', auth="public", website=True)
    def capsula(self, **post):
        # _logger.info("DOc info: %r" % document_id)
        _logger.info("DOc info: %r" % post)
        document = post.get('document')
        doc = document.sudo()
        # doc = request.env['documents.document'].sudo().browse([post])

        values = {
            'folder_name': doc.folder_id.name,
            'main_video': False,
            'document': doc,
        }
        if 'vimeo' in doc.url:
            owner = doc.partner_id
            owner_name = owner.name
            if owner.lastname:
                owner_name += " %s" % owner.lastname
            api_vimeo = "https://vimeo.com/api/oembed.json?url={}".format(
                doc.url)
            try:
                data = requests.get(api_vimeo)
                if data.status_code == 200:
                    data = data.json()
                    src = data.get('html').split(' ')[1]
                    link = src.replace('src="', '').replace('"', '')
                    values['data'] = {
                        'name': data.get('title'),
                        'author_name': data.get('author_name'),
                        'owner_name': owner_name,
                        'description': data.get('description'),
                        'embed_code': link,
                    }
            except requests.exceptions.ConnectionError as e:
                pass

        _logger.info("Capuslas info: %r" % values)
        return request.render("elearning_features.capsula_main_page", values)

    @http.route('/web/shared/video/<int:video_id>', type='http', auth="public", website=True)
    def video_shared(self, video_id):
        print("ID = %s" % video_id)
        document = request.env['documents.document'].sudo().browse([int(
            video_id)])
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')

        values = {
            'name': document.name,
            'video_id': extract.video_id(document.url)
        }
        print("Datos: %r" % values)
        return request.render("elearning_features.video_shared", values)

    @http.route(['/attachment/download'], type='http', auth="user")
    # @serialize_exception
    def download_document(self, document_id):
        document = request.env['documents.document'].sudo().browse(int(
            document_id))

        if document.type == "url":
            return werkzeug.utils.redirect(document.url)
        elif document.type == "binary":
            encode_content = base64.b64decode(document.datas)
            data = BytesIO(encode_content)
            return http.send_file(
                data, filename=document.name, as_attachment=True)
        else:
            return request.not_found()

    @http.route('/glosario', type='http', auth="public", website=True)
    def glosary(self, **post):
        glosary_ids = request.env['website.glosary'].sudo().search([
            ('id', '>', 0)
        ])
        glosary_dict = {}
        for glosary in glosary_ids:
            if glosary.letter in glosary_dict:
                glosary_dict[glosary.letter].append({
                    'id': glosary.id,
                    'name': glosary.name,
                    'definition': glosary.definition,
                    'letter': glosary.letter,
                    'ancle': "#accord_%s" % glosary.letter,
                    'css_id': "accord_%s" % glosary.letter,
                })
            else:
                glosary_dict[glosary.letter] = [{
                    'id': glosary.id,
                    'name': glosary.name,
                    'definition': glosary.definition,
                    'letter': glosary.letter,
                    'ancle': "#accord_%s" % glosary.letter,
                    'css_id': "accord_%s" % glosary.letter,
                }]
        values = {
            'letters': list(string.ascii_uppercase),
            'glosary_dict': glosary_dict,
        }

        return request.render("elearning_features.glosary", values)

    @http.route('/cursos/get_document_slide', type='http', auth='public')
    def get_document_slide(self, xmlid=None, model='slide.slide', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None,special_access=False, **kw):

        status, headers, content = request.env['ir.http'].binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token, special_access=special_access)

        if status != 200:
            return request.env['ir.http']._response_by_status(status, headers, content)
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie('fileToken', token)
        return response

    @http.route(['/search/faqs'], type='http', auth="public")
    def search_faqs(self, **post):
        suggestion_list, product, product_list_name = [], [], []

        if post:
            for suggestion in post.get('query').split(" "):
                product_list = request.env['website.help.center'].search(([
                    ('active', '=', True), '|',
                    ('name', 'ilike', suggestion),
                    ('faq', 'ilike', suggestion),
                ]))
                read_prod = product_list.read(['name', 'faq', 'id'])
                suggestion_list = suggestion_list + read_prod

        for line in suggestion_list:
            prod_str = line['name']
            if prod_str not in product_list_name:
                product.append({
                    'product': line['name'],
                    'faq': line['faq'],
                    'id': line['id']
                })
                product_list_name.append(prod_str)

        data = {
            'status': True,
            'error': None,
            'data': {'product': product},
        }
        return json.dumps(data)

    def _process_registration_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    # @http.route([
    #     '''/eventos/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/registration/confirm'''], type='http', auth="public", methods=['POST'], website=True)
    # def registration_confirm(self, event, **post):
    #     if not event.can_access_from_current_website():
    #         raise werkzeug.exceptions.NotFound()
    #
    #     Attendees = request.env['event.registration']
    #     # MailRegisttration = request.env['event.mail.registration'].sudo()
    #     # EventMail = request.env['event.mail'].sudo()
    #     registrations = self._process_registration_details(post)
    #
    #     for registration in registrations:
    #         registration['event_id'] = event
    #         # Attendees += Attendees.sudo().create(
    #         #     Attendees._prepare_attendee_values(registration))
    #     attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
    #
    #     for attendee in attendees_sudo:
    #         attendee.sudo().confirm_registration()
    #
    #     mail_template = request.env.ref(
    #         'elearning_features.event_subscription').sudo()
    #     event.sudo().mail_attendees(mail_template.id, force_send=True)
    #
    #     urls = event._get_event_resource_urls()
    #     return request.render("website_event.registration_complete", {
    #         'attendees': attendees_sudo,
    #         'event': event,
    #         'google_url': urls.get('google_url'),
    #         'iCal_url': urls.get('iCal_url')
    #     })


class Survey(Survey):

    def _prepare_survey_finished_values(self, survey, answer, token=False):
        values = {'survey': survey, 'answer': answer}

        if token:
            values['token'] = token
        if survey.scoring_type != 'no_scoring' and survey.certificate:
            answer_perf = survey._get_answers_correctness(answer)[answer]
            values['graph_data'] = json.dumps([
                {"text": "Correcta", "count": answer_perf['correct']},
                {"text": "Parcialmente", "count": answer_perf['partial']},
                {"text": "Incorrecta", "count": answer_perf['incorrect']},
                {"text": "Sin respuesta", "count": answer_perf['skipped']}
            ])
        if answer:
            channel_tag_ref = "elearning_features."
            if 0 < answer.quizz_score < 20:
                channel_tag_ref += "slide_channel_tag_survey_level_basic"
            elif 20 < answer.quizz_score < 40:
                channel_tag_ref += "slide_channel_tag_survey_level_middle"
            elif 40 < answer.quizz_score < 60:
                channel_tag_ref += "slide_channel_tag_survey_level_middle_high"
            elif 60 < answer.quizz_score < 80:
                channel_tag_ref += "slide_channel_tag_survey_level_agil"
            else:
                channel_tag_ref += "slide_channel_tag_survey_level_pro"

            channel_tag_ids = request.env.ref(channel_tag_ref).ids
            channels = request.env['slide.channel'].sudo().search([
                ('survey_tag_ids', 'in', channel_tag_ids)
            ])
            if channels:
                values['channels'] = channels.sorted(
                    'create_date', reverse=True)
                values['tags'] = channel_tag_ids
        return values

    @http.route(['/survey/<int:survey_id>/get_certification'], type='http', auth='user', methods=['GET'], website=True)
    def survey_get_certification(self, survey_id, **kwargs):
        """ The certification document can be downloaded as long as the user has succeeded the certification """
        survey = request.env['survey.survey'].sudo().search([
            ('id', '=', survey_id),
            ('certificate', '=', True)
        ])

        if not survey:
            # no certification found
            return werkzeug.utils.redirect("/")

        succeeded_attempt = request.env['survey.user_input'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('survey_id', '=', survey_id),
            ('quizz_passed', '=', True)
        ], limit=1)

        if not succeeded_attempt:
            raise UserError(_("The user has not succeeded the certification"))

        report_sudo = request.env.ref('survey.certification_report').sudo()

        report = report_sudo.render_qweb_pdf([succeeded_attempt.id], data={'report_type': 'pdf'})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(report)),
        ]
        reporthttpheaders.append(('Content-Disposition', content_disposition('Certificado.pdf')))
        return request.make_response(report, headers=reporthttpheaders)


class WebsiteBlog(WebsiteBlog):

    @http.route([
        '''/blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    ], type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        if not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        BlogPost = request.env['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        pager_url = "/blogpost/%s" % blog_post.id

        pager = request.website.pager(
            url=pager_url,
            total=len(blog_post.website_message_ids),
            page=page,
            step=self._post_comment_per_page,
            scope=7
        )
        pager_begin = (page - 1) * self._post_comment_per_page
        pager_end = page * self._post_comment_per_page
        comments = blog_post.website_message_ids[pager_begin:pager_end]

        domain = request.website.website_domain()
        blogs = blog.search(domain, order="create_date, id asc")

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin, date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/blog/%s/post/%s" % (slug(blog_post.blog_id), slug(blog_post)), code=301)

        tags = request.env['blog.tag'].search([])

        # Find next Post
        blog_post_domain = [('blog_id', '=', blog.id)]
        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = BlogPost.search(blog_post_domain)

        if blog_post not in all_post:
            return request.redirect("/blog/%s" % (slug(blog_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        related_domain = request.website.website_domain()

        related_domain += [('blog_id', '=', blog.id)]

        related_posts = BlogPost.search(domain,limit=11, order="is_published desc, post_date desc, id asc")


        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blogs': blogs,
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'date': date_begin,
            'blog_url': blog_url,
            'pager': pager,
            'related_posts': related_posts,
            'comments': comments,
        }

        # import ipdb; ipdb.set_trace()
        response = request.render("website_blog.blog_post_complete", values)

        request.session[request.session.sid] = request.session.get(request.session.sid, [])
        if not (blog_post.id in request.session[request.session.sid]):
            request.session[request.session.sid].append(blog_post.id)
            # Increase counter
            blog_post.sudo().write({
                'visits': blog_post.visits + 1,
                'write_date': blog_post.write_date,
            })
        return response


class WebsiteSlides(WebsiteSlides):

    def _extract_channel_tag_search(self, **post):
        tags = request.env['slide.channel.tag']
        for key in (_key for _key in post if _key.startswith('channel_tag_group_id_')):
            group_id, tag_id = False, False
            try:
                group_id = int(key.lstrip('channel_tag_group_id_'))
                tag_id = int(post[key])
            except:
                pass
            else:
                search_tag = request.env['slide.channel.tag'].search([('id', '=', tag_id), ('group_id', '=', group_id)]).exists()
                if search_tag:
                    tags |= search_tag
        return tags

    def _build_channel_domain(self, base_domain, slide_type=None, my=False, **post):
        search_term = post.get('search')
        channel_tag_id = post.get('channel_tag_id')
        tags = self._extract_channel_tag_search(**post)

        domain = base_domain
        if search_term:
            domain = expression.AND([
                domain,
                ['|', ('name', 'ilike', search_term), ('description', 'ilike', search_term)]])
        if channel_tag_id:
            domain = expression.AND([domain, [('tag_ids', 'in', [channel_tag_id])]])
        elif tags:
            domain = expression.AND([domain, [('tag_ids', 'in', tags.ids)]])

        if slide_type and 'nbr_%s' % slide_type in request.env['slide.channel']:
            domain = expression.AND([domain, [('nbr_%s' % slide_type, '>', 0)]])

        if my:
            domain = expression.AND([domain, [('partner_ids', '=', request.env.user.partner_id.id)]])
        return domain

    def sitemap_slide(env, rule, qs):
        Channel = env['slide.channel']
        dom = sitemap_qs2dom(qs=qs, route='/cursos/', field=Channel._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = '/cursos/%s' % slug(channel)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    def _prepare_channels_from_survey_result(self, user):
        values = {'channels': [], 'skipp_tags': []}
        member_ids = request.env['slide.channel.partner'].sudo().search_read([
            #('completed', '=', True), TODO: No encuetra campo 07 septiembre
            ('partner_id', '=', user.partner_id.id),
        ], ['channel_id'])
        channel_completed = [m.get('channel_id')[0] for m in member_ids]
        academy_survey = request.env.ref("elearning_features.survey_profile").id
        answer = request.env['survey.user_input'].sudo().search([
            ('survey_id', '=', academy_survey),
            ('partner_id', '=', user.partner_id.id),
        ], limit=1)

        if not answer:
            return values

        channel_tag_ref = "elearning_features."
        if 0 < answer.quizz_score < 20:
            channel_tag_ref += "slide_channel_tag_survey_level_basic"
        elif 20 < answer.quizz_score < 40:
            channel_tag_ref += "slide_channel_tag_survey_level_middle"
        elif 40 < answer.quizz_score < 60:
            channel_tag_ref += "slide_channel_tag_survey_level_middle_high"
        elif 60 < answer.quizz_score < 80:
            channel_tag_ref += "slide_channel_tag_survey_level_agil"
        else:
            channel_tag_ref += "slide_channel_tag_survey_level_pro"

        # channel_ids = [p.channel_id.id for p in member_ids]
        # survey_tag_group = request.env.ref(
        #     "elearning_features.slide_channel_tag_group_survey")
        values['skipp_tags'] = []

        channel_tag_ids = request.env.ref(channel_tag_ref).ids
        channels = request.env['slide.channel'].sudo().search([
            ('id', 'not in', channel_completed),
            ('survey_tag_ids', 'in', channel_tag_ids),
        ])
        if channels:
            values['channels'] = channels.sorted('create_date', reverse=True)

        return values

    @http.route(['/cursos', '/slides'], type='http', auth="public", website=True)
    def slides_channel_home(self, **post):
        """ Home page for eLearning platform. Is mainly a container page, does
        not allow search / filter. """
        domain = request.website.website_domain()
        domain.append(('website_published', '=', True))
        _logger.info("Slide domain: %r" % domain)
        channels_all = request.env['slide.channel'].sudo().search(domain)
        if not request.env.user._is_public():
            channels_my = channels_all.filtered(
                lambda channel: channel.is_member).sorted(
                'completion', reverse=True)[:3]
        else:
            channels_my = request.env['slide.channel'].sudo()
        channels_popular = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest = channels_all.sorted('create_date', reverse=True)[:20]

        achievements = request.env['gamification.badge.user'].sudo().search([
            ('badge_id.is_published', '=', True)], limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                # ('category', '=', 'slides'),  TODO: No encuetra campo 07 septiembre
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')

        values = self._prepare_user_values(**post)
        survey = self._prepare_channels_from_survey_result(request.env.user)
        channels_basics = request.env['slide.channel'].sudo().search(domain+[
            ('tag_ids', 'in', [1]),
        ])
        channels_intermediate = request.env['slide.channel'].sudo().search(domain+[
            ('tag_ids', 'in', [21]),
        ])
        channels_advanced = request.env['slide.channel'].sudo().search(domain+[
            ('tag_ids', 'in', [30]),
        ])
        values.update({
            'channels_my': channels_my,
            'channels_popular': channels_popular,
            'channels_newest': channels_newest,
            'channels_basics': channels_basics,
            'channels_intermediate': channels_intermediate,
            'channels_advanced': channels_advanced,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'survey_channels': survey.get('channels'),
            'skipp_tags': survey.get('skipp_tags'),
            # 'channels_last':channels_last,
        })

        return request.render('website_slides.courses_home', values)

    @http.route(['/cursos/todos', '/cursos/all', '/slides/all'], type='http', auth="public", website=True)
    def slides_channel_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type,
                                            my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels = request.env['slide.channel'].sudo().search(domain, order=order)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
            'slugify_tags': self._slugify_tags,
            'slide_query_url': QueryURL('/slides/all', ['tag']),
        })

        return request.render('website_slides.courses_all', values)

    @http.route([
        '/slides/<model("slide.channel"):channel>',
        '/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
        '/cursos/<model("slide.channel"):channel>',
        '/cursos/<model("slide.channel"):channel>/page/<int:page>',
        '/cursos/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/cursos/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/cursos/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/cursos/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>'
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def channel(self, channel, category=None, tag=None, page=1, slide_type=None,
                uncategorized=False, sorting=None, search=None, **kw):
        if not channel.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        domain = self._get_channel_slides_base_domain(channel)

        pager_url = "/cursos/%s" % (channel.id)
        pager_args = {}
        slide_types = dict(request.env['slide.slide']._fields[
                               'slide_type']._description_selection(
            request.env))

        if search:
            domain += [
                '|', '|',
                ('name', 'ilike', search),
                ('description', 'ilike', search),
                ('html_content', 'ilike', search)]
            pager_args['search'] = search
        else:
            if category:
                domain += [('category_id', '=', category.id)]
                pager_url += "/category/%s" % category.id
            elif tag:
                domain += [('tag_ids.id', '=', tag.id)]
                pager_url += "/tag/%s" % tag.id
            if uncategorized:
                domain += [('category_id', '=', False)]
                pager_url += "?uncategorized=1"
            elif slide_type:
                domain += [('slide_type', '=', slide_type)]
                pager_url += "?slide_type=%s" % slide_type

        # sorting criterion
        if channel.channel_type == 'documentation':
            actual_sorting = sorting if sorting and sorting in request.env[
                'slide.slide']._order_by_strategy else channel.promote_strategy
        else:
            actual_sorting = 'sequence'
        order = request.env['slide.slide']._order_by_strategy[actual_sorting]
        pager_args['sorting'] = actual_sorting

        slide_count = request.env['slide.slide'].sudo().search_count(domain)
        page_count = math.ceil(slide_count / self._slides_per_page)
        pager = request.website.pager(url=pager_url, total=slide_count,
                                      page=page,
                                      step=self._slides_per_page,
                                      url_args=pager_args,
                                      scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

        query_string = None
        if category:
            query_string = "?search_category=%s" % category.id
        elif tag:
            query_string = "?search_tag=%s" % tag.id
        elif slide_type:
            query_string = "?search_slide_type=%s" % slide_type
        elif uncategorized:
            query_string = "?search_uncategorized=1"

        values = {
            'channel': channel,
            'main_object': channel,
            'active_tab': kw.get('active_tab', 'home'),
            # search
            'search_category': category,
            'search_tag': tag,
            'search_slide_type': slide_type,
            'search_uncategorized': uncategorized,
            'query_string': query_string,
            'slide_types': slide_types,
            'sorting': actual_sorting,
            'search': search,
            # chatter
            'rating_avg': channel.rating_avg,
            'rating_count': channel.rating_count,
            # display data
            'user': request.env.user,
            'pager': pager,
            'is_public_user': request.website.is_public_user(),
            # display upload modal
            'enable_slide_upload': 'enable_slide_upload' in kw,
        }
        if not request.env.user._is_public():
            last_message = request.env['mail.message'].search([
                ('model', '=', channel._name),
                ('res_id', '=', channel.id),
                ('author_id', '=', request.env.user.partner_id.id),
                ('message_type', '=', 'comment'),
                # ('website_published', '=', True)
            ], order='write_date DESC', limit=1)
            if last_message:
                last_message_values = \
                last_message.read(['body', 'rating_value', 'attachment_ids'])[0]
                last_message_attachment_ids = last_message_values.pop(
                    'attachment_ids', [])
                if last_message_attachment_ids:
                    last_message_attachment_ids = json.dumps(
                        request.env['ir.attachment'].browse(
                            last_message_attachment_ids).sudo().read(
                            ['id', 'name', 'mimetype', 'file_size',
                             'access_token']
                        ))
            else:
                last_message_values = {}
                last_message_attachment_ids = []
            values.update({
                'last_message_id': last_message_values.get('id'),
                'last_message': tools.html2plaintext(
                    last_message_values.get('body', '')),
                'last_rating_value': last_message_values.get('rating_value'),
                'last_message_attachment_ids': last_message_attachment_ids,
            })
            if channel.can_review:
                values.update({
                    'message_post_hash': channel._sign_token(
                        request.env.user.partner_id.id),
                    'message_post_pid': request.env.user.partner_id.id,
                })

        # fetch slides and handle uncategorized slides; done as sudo because we want to display all
        # of them but unreachable ones won't be clickable (+ slide controller will crash anyway)
        # documentation mode may display less slides than content by category but overhead of
        # computation is reasonable
        values['slide_promoted'] = request.env['slide.slide'].sudo().search(
            domain, limit=1, order=order)
        values['category_data'] = channel._get_categorized_slides(
            domain, order,
            force_void=not category,
            limit=False if channel.channel_type != 'documentation' else self._slides_per_page if category else self._slides_per_category,
            offset=pager['offset'])
        values['channel_progress'] = self._get_channel_progress(channel,
                                                                include_quiz=True)

        # for sys admins: prepare data to install directly modules from eLearning when
        # uploading slides. Currently supporting only survey, because why not.
        if request.env.user.has_group('base.group_system'):
            module = request.env.ref('base.module_survey')
            if module.state != 'installed':
                values['modules_to_install'] = [{
                    'id': module.id,
                    'name': module.shortdesc,
                    'motivational': _(
                        'Evaluate and certificate your students.'),
                }]

        values = self._prepare_additional_channel_values(values, **kw)
        return request.render('website_slides.course_main', values)

    # SLIDE.CHANNEL UTILS
    # --------------------------------------------------

    @http.route(['/cursos/channel/add', '/slides/channel/add'], type='http', auth='user',
                methods=['POST'], website=True)
    def slide_channel_create(self, *args, **kw):
        channel = request.env['slide.channel'].sudo().create(
            self._slide_channel_prepare_values(**kw))
        return werkzeug.utils.redirect("/cursos/%s" % (slug(channel)))

    def _slide_channel_prepare_values(self, **kw):
        # `tag_ids` is a string representing a list of int with coma. i.e.: '2,5,7'
        # We don't want to allow user to create tags and tag groups on the fly.
        tag_ids = []
        if kw.get('tag_ids'):
            tag_ids = [int(item) for item in kw['tag_ids'].split(',')]

        return {
            'name': kw['name'],
            'description': kw.get('description'),
            'channel_type': kw.get('channel_type', 'documentation'),
            'user_id': request.env.user.id,
            'tag_ids': [(6, 0, tag_ids)],
            'allow_comment': bool(kw.get('allow_comment')),
        }

    @http.route(['/slides/channel/enroll', '/cursos/channel/enroll'], type='http', auth='public',
                website=True)
    def slide_channel_join_http(self, channel_id):
        # TDE FIXME: why 2 routes ?
        if not request.website.is_public_user():
            channel = request.env['slide.channel'].sudo().browse(int(channel_id))
            channel.action_add_member()
        return werkzeug.utils.redirect("/cursos/%s" % (slug(channel)))

    @http.route(['/slides/channel/join', '/cursos/channel/join'], type='json', auth='public',
                website=True)
    def slide_channel_join(self, channel_id):
        if request.website.is_public_user():
            return {'error': 'public_user', 'error_signup_allowed': request.env[
                                                                        'res.users'].sudo()._get_signup_invitation_scope() == 'b2c'}
        success = request.env['slide.channel'].sudo().browse(
            channel_id).action_add_member()
        if not success:
            return {'error': 'join_done'}
        return success

    @http.route(['/slides/channel/leave', '/cursos/channel/leave'], type='json', auth='user',
                website=True)
    def slide_channel_leave(self, channel_id):
        request.env['slide.channel'].sudo().browse(channel_id)._remove_membership(
            request.env.user.partner_id.ids)
        return True

    @http.route(['/cursos/channel/tag/search_read', '/slides/channel/tag/search_read'], type='json', auth='user',
                methods=['POST'], website=True)
    def slide_channel_tag_search_read(self, fields, domain):
        can_create = request.env['slide.channel.tag'].check_access_rights(
            'create', raise_exception=False)
        return {
            'read_results': request.env['slide.channel.tag'].search_read(domain,
                                                                         fields),
            'can_create': can_create,
        }
    # --------------------------------------------------
    # SLIDE.SLIDE MAIN / SEARCH
    # --------------------------------------------------
    @http.route([
        '''/cursos/curso/<model("slide.slide", "[('website_id', 'in', (False, current_website_id))]"):slide>''',
        '''/slides/slide/<model("slide.slide", "[('website_id', 'in', (False, current_website_id))]"):slide>'''],
        type='http', auth="public", website=True)
    def slide_view(self, slide, **kwargs):
        return super().slide_view(slide, **kwargs)
        # if not slide.channel_id.can_access_from_current_website() or not slide.active:
        #     raise werkzeug.exceptions.NotFound()
        # self._set_viewed_slide(slide)
        #
        # values = self._get_slide_detail(slide)
        # # quiz-specific: update with karma and quiz information
        # if slide.question_ids:
        #     values.update(self._get_slide_quiz_data(slide))
        # # sidebar: update with user channel progress
        # values['channel_progress'] = self._get_channel_progress(
        #     slide.channel_id, include_quiz=True)
        #
        # # Allows to have breadcrumb for the previously used filter
        # values.update({
        #     'search_category': slide.category_id if kwargs.get(
        #         'search_category') else None,
        #     'search_tag': request.env['slide.tag'].browse(
        #         int(kwargs.get('search_tag'))) if kwargs.get(
        #         'search_tag') else None,
        #     'slide_types': dict(request.env['slide.slide']._fields[
        #                             'slide_type']._description_selection(
        #         request.env)) if kwargs.get('search_slide_type') else None,
        #     'search_slide_type': kwargs.get('search_slide_type'),
        #     'search_uncategorized': kwargs.get('search_uncategorized')
        # })
        #
        # values['channel'] = slide.channel_id
        # values = self._prepare_additional_channel_values(values, **kwargs)
        # values.pop('channel', None)
        #
        # values['signup_allowed'] = request.env[
        #                                'res.users'].sudo()._get_signup_invitation_scope() == 'b2c'
        #
        # if kwargs.get('fullscreen') == '1':
        #     return request.render("website_slides.slide_fullscreen", values)
        # return request.render("website_slides.slide_main", values)

    # SLIDE.SLIDE UTILS
    # --------------------------------------------------

    @http.route([
        '/cursos/curso/<model("slide.slide"):slide>/set_completed',
        '/slides/slide/<model("slide.slide"):slide>/set_completed'],
                website=True, type="http", auth="user")
    def slide_set_completed_and_redirect(self, slide, next_slide_id=None):
        self._set_completed_slide(slide)
        next_slide = None
        if next_slide_id:
            next_slide = self._fetch_slide(next_slide_id).get('slide', None)
        return werkzeug.utils.redirect("/cursos/curso/%s" % (
            slug(next_slide) if next_slide else slug(slide)))

    @http.route(['/slides/slide/like', '/cursos/curso/like'], type='json', auth="public", website=True)
    def slide_like(self, slide_id, upvote):
        if request.website.is_public_user():
            return {'error': 'public_user', 'error_signup_allowed': request.env[
                                                                        'res.users'].sudo()._get_signup_invitation_scope() == 'b2c'}
        slide_partners = request.env['slide.slide.partner'].sudo().search([
            ('slide_id', '=', slide_id),
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        if (upvote and slide_partners.vote == 1) or (
                not upvote and slide_partners.vote == -1):
            return {'error': 'vote_done'}
        # check slide access
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        # check slide operation
        slide = fetch_res['slide']
        if not slide.channel_id.is_member:
            return {'error': 'channel_membership_required'}
        if not slide.channel_id.allow_comment:
            return {'error': 'channel_comment_disabled'}
        if not slide.channel_id.can_vote:
            return {'error': 'channel_karma_required'}
        if upvote:
            slide.action_like()
        else:
            slide.action_dislike()
        slide.invalidate_cache()
        return slide.read(['likes', 'dislikes', 'user_vote'])[0]

    @http.route(['/slides/slide/archive', '/cursos/curso/archive'], type='json', auth='user', website=True)
    def slide_archive(self, slide_id):
        """ This route allows channel publishers to archive slides.
        It has to be done in sudo mode since only website_publishers can write on slides in ACLs """
        slide = request.env['slide.slide'].browse(int(slide_id))
        if slide.channel_id.can_publish:
            slide.sudo().active = False
            return True

        return False

    @http.route([
        '/slides/slide/toggle_is_preview', '/cursos/curso/toggle_is_preview',
    ], type='json', auth='user', website=True)
    def slide_preview(self, slide_id):
        slide = request.env['slide.slide'].browse(int(slide_id))
        if slide.channel_id.can_publish:
            slide.is_preview = not slide.is_preview
        return slide.is_preview

    @http.route([
        '/slides/slide/send_share_email', '/cursos/curso/send_share_email',
    ], type='json', auth='user', website=True)
    def slide_send_share_email(self, slide_id, email, fullscreen=False):
        slide = request.env['slide.slide'].browse(int(slide_id))
        result = slide._send_share_email(email, fullscreen)
        return result

    @http.route([
        '/slides/slide/quiz/submit', '/cursos/curso/quiz/submit'], type="json",
        auth="public", website=True)
    def slide_quiz_submit(self, slide_id, answer_ids):
        if request.website.is_public_user():
            return {'error': 'public_user'}
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        slide = fetch_res['slide']

        if slide.user_membership_id.sudo().completed:
            return {'error': 'slide_quiz_done'}

        all_questions = request.env['slide.question'].sudo().search(
            [('slide_id', '=', slide.id)])

        user_answers = request.env['slide.answer'].sudo().search(
            [('id', 'in', answer_ids)])
        if user_answers.mapped('question_id') != all_questions:
            return {'error': 'slide_quiz_incomplete'}

        user_bad_answers = user_answers.filtered(
            lambda answer: not answer.is_correct)
        user_good_answers = user_answers - user_bad_answers

        self._set_viewed_slide(slide, quiz_attempts_inc=True)
        quiz_info = self._get_slide_quiz_partner_info(slide, quiz_done=True)

        karma = 1 if request.env.user.karma <= 0 else request.env.user.karma
        rank_progress = {}
        if not user_bad_answers:
            slide._action_set_quiz_done()
            #slide.action_set_completed()
            karma_min = request.env.user.rank_id.karma_min
            karma_next = request.env.user.next_rank_id.karma_min
            lower_bound = karma_min if karma_min > 0 else 1
            upper_bound = karma_next if karma_next > 0 else 1

            karma_rslt = karma - lower_bound
            karma_total = 1 if karma_rslt <= 0 else karma_rslt
            bound_rslt = upper_bound - lower_bound
            bound_total = 1 if bound_rslt <= 0 else bound_rslt
            rank_progress = {
                'lowerBound': lower_bound,
                'upperBound': upper_bound,
                'currentKarma': karma,
                'motivational': request.env.user.next_rank_id.description_motivational,
                'progress': 100
                # 'progress': 100 * (karma_total / bound_total)
            }
        return {
            'goodAnswers': user_good_answers.ids,
            'badAnswers': user_bad_answers.ids,
            'completed': slide.user_membership_id.sudo().completed,
            'channel_completion': slide.channel_id.completion,
            'quizKarmaWon': quiz_info['quiz_karma_won'],
            'quizKarmaGain': quiz_info['quiz_karma_gain'],
            'quizAttemptsCount': quiz_info['quiz_attempts_count'],
            'rankProgress': rank_progress,
        }

    # --------------------------------------------------
    # CATEGORY MANAGEMENT
    # --------------------------------------------------

    @http.route([
        '/cursos/category/search_read', '/slides/category/search_read'],
        type='json', auth='user', methods=['POST'], website=True)
    def slide_category_search_read(self, fields, domain):
        category_slide_domain = domain if domain else []
        category_slide_domain = expression.AND(
            [category_slide_domain, [('is_category', '=', True)]])
        can_create = request.env['slide.slide'].check_access_rights('create',
                                                                    raise_exception=False)
        return {
            'read_results': request.env['slide.slide'].search_read(
                category_slide_domain, fields),
            'can_create': can_create,
        }

    @http.route(['/slides/category/add', '/cursos/category/add'],
                type="http", website=True, auth="user", methods=['POST'])
    def slide_category_add(self, channel_id, name):
        """ Adds a category to the specified channel. Slide is added at the end
        of slide list based on sequence. """
        channel = request.env['slide.channel'].sudo().browse(int(channel_id))
        if not channel.can_upload or not channel.can_publish:
            raise werkzeug.exceptions.NotFound()

        request.env['slide.slide'].create(
            self._get_new_slide_category_values(channel, name))

        return werkzeug.utils.redirect("/cursos/%s" % (slug(channel)))

    # --------------------------------------------------
    # SLIDE.UPLOAD
    # --------------------------------------------------

    @http.route(['/cursos/prepare_preview', '/slides/prepare_preview'],
                type='json', auth='user', methods=['POST'], website=True)
    def prepare_preview(self, **data):
        Slide = request.env['slide.slide'].sudo()
        document_type, document_id = Slide._find_document_data_from_url(
            data['url'])
        preview = {}
        if not document_id:
            preview['error'] = _('Please enter valid youtube or google doc url')
            return preview
        existing_slide = Slide.search(
            [('channel_id', '=', int(data['channel_id'])),
             ('document_id', '=', document_id)], limit=1)
        if existing_slide:
            preview['error'] = _(
                'This video already exists in this channel on the following slide: %s') % existing_slide.name
            return preview
        values = Slide._parse_document_url(data['url'],
                                           only_preview_fields=True)
        if values.get('error'):
            preview['error'] = _(
                'Could not fetch data from url. Document or access right not available.\nHere is the received response: %s') % \
                               values['error']
            return preview
        return values

    @http.route(['/cursos/add_slide', '/slides/add_slide'], type='json',
                auth='user', methods=['POST'], website=True)
    def create_slide(self, *args, **post):
        # check the size only when we upload a file.
        if post.get('datas'):
            file_size = len(post['datas']) * 3 / 4  # base64
            if (file_size / 1024.0 / 1024.0) > 25:
                return {
                    'error': _('File is too big. File size cannot exceed 25MB')}

        values = dict((fname, post[fname]) for fname in
                      self._get_valid_slide_post_values() if post.get(fname))

        # handle exception during creation of slide and sent error notification to the client
        # otherwise client slide create dialog box continue processing even server fail to create a slide
        try:
            channel = request.env['slide.channel'].sudo().browse(values['channel_id'])
            can_upload = channel.can_upload
            can_publish = channel.can_publish
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        else:
            if not can_upload:
                return {'error': _('You cannot upload on this channel.')}

        if post.get('duration'):
            # minutes to hours conversion
            values['completion_time'] = int(post['duration']) / 60

        category = False
        # handle creation of new categories on the fly
        if post.get('category_id'):
            category_id = post['category_id'][0]
            if category_id == 0:
                category = request.env['slide.slide'].create(
                    self._get_new_slide_category_values(channel,
                                                        post['category_id'][1][
                                                            'name']))
                values['sequence'] = category.sequence + 1
            else:
                category = request.env['slide.slide'].sudo().browse(category_id)
                values.update({
                    'sequence': request.env['slide.slide'].browse(
                        post['category_id'][0]).sequence + 1
                })

        # create slide itself
        try:
            values['user_id'] = request.env.uid
            values['is_published'] = values.get('is_published',
                                                False) and can_publish
            slide = request.env['slide.slide'].sudo().create(values)
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        except Exception as e:
            _logger.error(e)
            return {'error': _(
                'Internal server error, please try again later or contact administrator.\nHere is the error message: %s') % e}

        # ensure correct ordering by re sequencing slides in front-end (backend should be ok thanks to list view)
        channel._resequence_slides(slide, force_category=category)

        redirect_url = "/cursos/curso/%s" % (slide.id)
        if channel.channel_type == "training" and not slide.slide_type == "webpage":
            redirect_url = "/cursos/%s" % (slug(channel))
        if slide.slide_type == 'webpage':
            redirect_url += "?enable_editor=1"
        if slide.slide_type == "quiz":
            action_id = request.env.ref('website_slides.slide_slide_action').id
            redirect_url = '/web#id=%s&action=%s&model=slide.slide&view_type=form' % (
            slide.id, action_id)
        return {
            'url': redirect_url,
            'channel_type': channel.channel_type,
            'slide_id': slide.id,
            'category_id': slide.category_id
        }

    def _get_valid_slide_post_values(self):
        return ['name', 'url', 'tag_ids', 'slide_type', 'channel_id',
                'is_preview',
                'mime_type', 'datas', 'description', 'image_1920',
                'is_published']

    @http.route(['/cursos/tag/search_read', '/slides/tag/search_read'],
                type='json', auth='user', methods=['POST'], website=True)
    def slide_tag_search_read(self, fields, domain):
        can_create = request.env['slide.tag'].check_access_rights('create',
                                                                  raise_exception=False)
        return {
            'read_results': request.env['slide.tag'].sudo().search_read(domain,
                                                                 fields),
            'can_create': can_create,
        }

    @http.route([
        '/slides/embed/<int:slide_id>',
        '/cursos/embed/<int:slide_id>'],
        type='http', auth='public', website=True, sitemap=False)
    def slides_embed(self, slide_id, page="1", **kw):
        # Note : don't use the 'model' in the route (use 'slide_id'), otherwise
        # if public cannot access the embedded slide, the error will be the
        # website.403 page instead of the one of the website_slides.embed_slide.
        # Do not forget the rendering here will be displayed in the embedded
        # iframe

        # determine if it is embedded from external web page
        referrer_url = request.httprequest.headers.get('Referer', '')
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        is_embedded = referrer_url and not bool(
            base_url in referrer_url) or False
        # try accessing slide, and display to corresponding template
        try:
            slide = request.env['slide.slide'].browse(slide_id)
            if is_embedded:
                request.env['slide.embed'].sudo()._add_embed_url(slide.id,
                                                                 referrer_url)
            values = self._get_slide_detail(slide)
            values['page'] = page
            values['is_embedded'] = is_embedded
            self._set_viewed_slide(slide)
            return request.render('website_slides.embed_slide', values)
        except AccessError:
            # TODO : please, make it clean one day, or find another secure way
            #  to detect if the slide can be embedded, and properly display
            #  the error message.
            return request.render('website_slides.embed_slide_forbidden', {})


class WebsiteEvent(WebsiteEventController):

    def sitemap_event(env, rule, qs):
        if not qs or qs.lower() in '/eventos':
            yield {'loc': '/eventos'}

    @http.route([
        '/event',
        '/event/page/<int:page>',
        '/events',
        '/events/page/<int:page>',
        '/evento',
        '/evento/page/<int:page>',
        '/eventos',
        '/eventos/page/<int:page>'],
        type='http', auth="public", website=True, sitemap=sitemap_event)
    def events(self, page=1, **searches):
        Event = request.env['event.event'].sudo()
        EventType = request.env['event.type'].sudo()

        searches.setdefault('search', '')
        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        website = request.website

        def sdn(date):
            return fields.Datetime.to_string(date.replace(hour=23, minute=59, second=59))

        def sd(date):
            return fields.Datetime.to_string(date)
        today = datetime.today()
        dates = [
            ['all', _('Next Events'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            ['week', _('This Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=6-today.weekday())))],
                0],
            ['nextweek', _('Next Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=7-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=13-today.weekday())))],
                0],
            ['month', _('This month'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['nextmonth', _('Next month'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['old', _('Past Events'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
                0],
        ]

        # search domains
        domain_search = {'website_specific': website.website_domain()}

        if searches['search']:
            domain_search['search'] = [('name', 'ilike', searches['search'])]

        current_date = None
        current_type = None
        current_country = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]

        if searches["type"] != 'all':
            current_type = EventType.browse(int(searches['type']))
            domain_search["type"] = [("event_type_id", "=", int(searches["type"]))]

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = request.env['res.country'].sudo().browse(int(searches['country']))
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]

        def dom_without(without):
            domain = [
                #('state', "in", ['draft', 'confirm', 'done']), TODO: Pendiente por arreglar state 07 septiembre
                ('website_published', '=', True),
            ]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = Event.search_count(dom_without('date') + date[2])

        domain = dom_without('type')
        types = Event.read_group(domain, ["id", "event_type_id"], groupby=["event_type_id"], orderby="event_type_id")
        types.insert(0, {
            'event_type_id_count': sum([int(type['event_type_id_count']) for type in types]),
            'event_type_id': ("all", _("All Categories"))
        })

        domain = dom_without('country')
        countries = Event.read_group(domain, ["id", "country_id"], groupby="country_id", orderby="country_id")
        countries.insert(0, {
            'country_id_count': sum([int(country['country_id_count']) for country in countries]),
            'country_id': ("all", _("All Countries"))
        })

        step = 12  # Number of events per page
        event_count = Event.search_count(dom_without("none"))
        pager = website.pager(
            url="/eventos",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order = 'date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'date_begin desc'
        if searches["country"] != 'all':   # if we are looking for a specific country
            order = 'is_online, ' + order  # show physical events first
        order = 'is_published desc, ' + order
        events = Event.search(dom_without("none"), limit=step, offset=pager['offset'], order=order)

        keep = QueryURL('/eventos', **{key: value for key, value in searches.items() if (key == 'search' or value != 'all')})

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events,  # event_ids used in website_event_track so we keep name as it is
            'dates': dates,
            'types': types,
            'countries': countries,
            'pager': pager,
            'searches': searches,
            'keep': keep,
        }

        if searches['date'] == 'old':
            # the only way to display this content is to set date=old so it must be canonical
            values['canonical_params'] = OrderedMultiDict([('date', 'old')])

        return request.render("website_event.index", values)

    @http.route([
        '''/eventos/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/page/<path:page>''',
        '''/evento/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/page/<path:page>''',
        '''/event/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/page/<path:page>'''
    ], type='http', auth="public", website=True, sitemap=False)
    def event_page(self, event, page, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        values = {
            'event': event,
        }

        if '.' not in page:
            page = 'website_event.%s' % page

        try:
            # Every event page view should have its own SEO.
            values['seo_object'] = request.website.get_template(page)
            values['main_object'] = event
        except ValueError:
            # page not found
            values['path'] = re.sub(r"^website_event\.", '', page)
            values['from_template'] = 'website_event.default_page'  # .strip('website_event.')
            page = request.website.is_publisher() and 'website.page_404' or 'http_routing.404'

        return request.render(page, values)

    @http.route([
        '''/eventos/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>''',
        '''/event/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>'''
    ], type='http', auth="public", website=True)
    def event(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        if event.menu_id and event.menu_id.child_id:
            target_url = event.menu_id.child_id[0].url
        else:
            target_url = '/eventos/%s/register' % str(event.id)
        if post.get('enable_editor') == '1':
            target_url += '?enable_editor=1'
        return request.redirect(target_url)

    @http.route([
        '''/eventos/<model("event.event", "[('website_id', 'in', ( False, current_website_id))]"):event>/register''',
        '''/event/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/register''',
    ], type='http', auth="public", website=True, sitemap=False)
    def event_register(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        urls = event._get_event_resource_urls()
        values = {
            'event': event,
            'main_object': event,
            'range': range,
            'registrable': event.sudo()._is_event_registrable(),
            'google_url': urls.get('google_url'),
            'iCal_url': urls.get('iCal_url'),
        }
        return request.render("website_event.event_description_full", values)

    @http.route(['/event/add_event', '/eventos/add_event'],
                type='json', auth="user", methods=['POST'], website=True)
    def add_event(self, event_name="New Event", **kwargs):
        event = self._add_event(event_name, request.context)
        return "/eventos/%s/register?enable_editor=1" % slug(event)

    def _add_event(self, event_name=None, context=None, **kwargs):
        if not event_name:
            event_name = _("New Event")
        date_begin = datetime.today() + timedelta(days=(14))
        vals = {
            'name': event_name,
            'date_begin': fields.Date.to_string(date_begin),
            'date_end': fields.Date.to_string((date_begin + timedelta(days=(1)))),
            'seats_available': 1000,
            'website_id': request.website.id,
        }
        return request.env['event.event'].with_context(context or {}).create(vals)

    def get_formated_date(self, event):
        start_date = fields.Datetime.from_string(event.date_begin).date()
        end_date = fields.Datetime.from_string(event.date_end).date()
        month = babel.dates.get_month_names('abbreviated', locale=get_lang(
            event.env).code)[start_date.month]
        return '%s %s%s' % (month, start_date.strftime("%e"), (
                end_date != start_date and ("-" + end_date.strftime("%e")) or
                ""))

    @http.route([
        '/event/get_country_event_list',
        '/evento/get_country_event_list',
    ], type='json', auth='public', website=True)
    def get_country_events(self, **post):
        Event = request.env['event.event'].sudo()
        country_code = request.session['geoip'].get('country_code')
        result = {'events': [], 'country': False}
        events = None
        domain = request.website.website_domain()
        if country_code:
            country = request.env['res.country'].sudo().search([
                ('code', '=', country_code)], limit=1)
            events = Event.search(domain + [
                '|', ('address_id', '=', None),
                ('country_id.code', '=', country_code),
                ('date_begin', '>=', '%s 00:00:00' % fields.Date.today()),
                ('state', '=', 'confirm')
            ], order="date_begin")
        if not events:
            events = Event.search(domain + [
                ('date_begin', '>=', '%s 00:00:00' % fields.Date.today()),
                ('state', '=', 'confirm')
            ], order="date_begin")
        for event in events:
            if country_code and event.country_id.code == country_code:
                result['country'] = country
            result['events'].append({
                "date": self.get_formated_date(event),
                "event": event,
                "url": event.website_url})
        return request.env['ir.ui.view'].render_template(
            "website_event.country_events_list", result)

    def _process_tickets_details(self, data):
        nb_register = int(data.get('nb_register-0', 0))
        if nb_register:
            return [{
                'id': 0,
                'name': 'Registration',
                'quantity': nb_register,
                'price': 1000,
            }]
        return []

    @http.route([
        '/event/<model("event.event"):event>/registration/new',
        '/eventos/<model("event.event"):event>/registration/new',
    ], type='json', auth="public", methods=['POST'], website=True)
    def registration_new(self, event, **post):
        tickets = self._process_tickets_details(post)
        availability_check = True
        if event.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket['quantity']
            if event.seats_available < ordered_seats:
                availability_check = False
        if not tickets:
            return False
        default_first_attendee = {}
        if not request.env.user._is_public():
            default_first_attendee = {
                "name": request.env.user.name,
                "email": request.env.user.email,
                "phone": request.env.user.mobile or request.env.user.phone,
            }
        else:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor.email:
                default_first_attendee = {
                    "name": visitor.display_name,
                    "email": visitor.email,
                    "phone": visitor.mobile,
                }

        values = {
            'tickets': tickets,
            'event': event,
            'availability_check': availability_check,
            'default_first_attendee': default_first_attendee,
        }
        return request.env['ir.ui.view']._render_template(
            "website_event.registration_attendee_details", values)

    def _process_registration_details(self, details):
        ''' Process data posted from the attendee details form. '''
        registrations = {}
        global_values = {}
        for key, value in details.items():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                registrations.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
        return list(registrations.values())

    @http.route([
        '''/event/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/registration/confirm''',
        '''/eventos/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/registration/confirm'''
    ], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        Attendees = request.env['event.registration']
        registrations = self._process_attendees_form(event, post)

        for registration in registrations:
            registration['event_id'] = event
            # Attendees += Attendees.sudo().create(
            #     Attendees._prepare_attendee_values(registration))
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)

        urls = event._get_event_resource_urls()
        return request.render("website_event.registration_complete", {
            'attendees': attendees_sudo,
            'event': event,
            'google_url': urls.get('google_url'),
            'iCal_url': urls.get('iCal_url')
        })
