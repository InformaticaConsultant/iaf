from odoo import api, fields, models
import logging

class InheritResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    client_id = fields.Text('Client ID.')
    client_secret = fields.Text('Client Secret')
    redirect_uri = fields.Text('Redirect URI')
    okta_auth_server_uri = fields.Char('Okta Authorization URI')
    
    def set_values(self):
        super(InheritResConfigSettings, self).set_values()

        IrConfig = self.env['ir.config_parameter'].sudo()
        IrConfig.set_param('nexus_okta_sso.client_id', self.client_id)
        IrConfig.set_param('nexus_okta_sso.client_secret', self.client_secret)
        IrConfig.set_param('nexus_okta_sso.redirect_uri', self.redirect_uri)
        IrConfig.set_param('nexus_okta_sso.okta_auth_server_uri',
                           self.okta_auth_server_uri)

    @api.model
    def get_values(self):
        res = super(InheritResConfigSettings, self).get_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        res['client_id'] = IrConfig.get_param('nexus_okta_sso.client_id')
        res['client_secret'] = IrConfig.get_param('nexus_okta_sso.client_secret')
        res['redirect_uri'] = IrConfig.get_param('nexus_okta_sso.redirect_uri')
        res['okta_auth_server_uri'] = IrConfig.get_param(
            'nexus_okta_sso.okta_auth_server_uri')
        return res

    def _get_client_id(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'nexus_okta_sso.client_id')

    def _get_client_secret(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'nexus_okta_sso.client_secret')
    
    def _get_redirect_uri(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'nexus_okta_sso.redirect_uri')

    def _get_okta_auth_server_uri(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'nexus_okta_sso.okta_auth_server_uri')

    @api.model
    def okta_authorize_url(self):
        client_id = self._get_client_id()
        redirect_url = self._get_redirect_uri()
        response_type = "code"
        state = "okta_login"
        scope = "openid profile email address phone"
        authorization_uri = self._get_okta_auth_server_uri()

        data = (client_id, response_type, redirect_url, scope, state)
        url = "{}/oauth2/default/v1/authorize?client_id={}&response_type=code&" \
              "scope={}&redirect_uri={}&state=okta_login".format(
            authorization_uri, client_id, scope, redirect_url)
        return url