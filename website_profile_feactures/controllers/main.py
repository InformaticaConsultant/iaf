# -*- coding: utf-8 -*-

import logging
import werkzeug
import json
import math
from odoo import http, _
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound

_logger = logging.getLogger(__name__)


PROFILE_TOTAL_POINTS = 56


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

        countries = request.env['res.country'].sudo().search([('code', '=', 'DO')])
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
            percent = 100 * float(pup)/float(PROFILE_TOTAL_POINTS)
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
            'towns':  request.env['res.country.town'].search([
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
