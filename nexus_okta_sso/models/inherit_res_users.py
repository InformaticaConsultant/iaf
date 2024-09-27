from odoo import api, fields, models, _
import requests
import werkzeug
import werkzeug.utils
from odoo.exceptions import UserError
import logging
import json as js

_logger = logging.getLogger(__name__)


class InheritResUsers(models.Model):
    _inherit = 'res.users'

    def login_office_user(self, code):
        _logger.info("######################################")
        res_config_settings_obj = self.env['res.config.settings'].sudo()
        client_id = res_config_settings_obj._get_client_id()
        client_secret = res_config_settings_obj._get_client_secret()
        redirect_url = res_config_settings_obj._get_redirect_uri()
        auth_server_url = res_config_settings_obj._get_okta_auth_server_uri()

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_url,
            "code": code,
            "scope": "openid profile email address phone",
            "grant_type": "authorization_code",
        }
        try:
            response = requests.post("{}/oauth2/default/v1/token".format(
                auth_server_url), data=data)
            _logger.info("URL FOR TOKEN IS {}".format(response.url))
        except Exception as ex:
            _logger.info(str(ex))
            raise UserError("Internet connected failed!")
        json_data = js.loads(response.text)
        if "access_token" in json_data:
            access_token = json_data['access_token']
            token_type = json_data['token_type']
            auth_token = token_type
            head = {
                "Authorization": auth_token + " " + access_token,
            }
            response = requests.get("{}/oauth2/default/v1/userinfo".format(
                auth_server_url), headers=head)
            json = js.loads(response.text)
            _logger.info("JSON INFO: %r" % json)
            _logger.info("Company INFO: %r" % self.env.company.ids)
            _logger.info("Company INFO: %r" % self.env.context)
            if 'error' not in json:
                _logger.info("OKTA INFO: %r" % json)
                """
                OKTA INFO: {
                    'name': 'JUAN CARLOS PARRA MORILLO', 
                    'email': 'juparra@bpd.com.do', 
                    'given_name': 'JUAN CARLOS', 
                    'family_name': 'PARRA MORILLO',
                }
                """
                _name = json['name']
                _email = json['email']
                user = self.env['res.users'].sudo().search([
                    ('login', '=', _email)])
                if not user:
                    user = self.env['res.users'].sudo().search([
                        ('login', '=', _email),
                        ('active', '=', False),
                    ])

                    if user:
                        user.write({'active': True})
                        user.partner_id.write({
                            'name': json.get('given_name'),
                            'lastname': json.get('family_name'),
                            'company_id': self.env.company.id,
                        })
                if not user:
                    partner = self.env['res.partner'].search([
                        ('email', '=', _email)])
                    if not partner:
                        partner = self.env['res.partner'].create({
                            'name': json.get('given_name'),
                            'lastname': json.get('family_name'),
                            'email': _email,
                            'company_id': self.env.company.id,
                        })

                    template_user = self.env.ref(
                        "base.template_portal_user_id")
                    user_values = {
                        'name': _name,
                        'login': partner.email,
                        'partner_id': partner.id,
                        'company_id': self.env.company.id,
                        'groups_id': template_user.groups_id,
                        'active': True,
                        'is_account_confirmed': True,
                    }

                    _logger.info("USER COPY INFO: %r" % user_values)
                    user = self.env['res.users'].with_context(
                        no_reset_password=True).create(user_values)
                    if user:
                        user._send_account_validation_email()
                        _logger.info("PARTNER INFO: %r - %r" % (json.get(
                            'given_name'), json.get('family_name')))
                        user.partner_id.write({
                            'name': json.get('given_name'),
                            'lastname': json.get('family_name'),
                            'company_id': self.env.company.id,
                        })
                return user
            else:
                return False
        else:
            return False
