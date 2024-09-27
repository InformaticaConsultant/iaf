import logging
import requests
import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home as WebHome

_logger = logging.getLogger(__name__)


class OktaController(http.Controller):

    @http.route('/okta/signin', type="http", auth="public")
    def okta_signin(self, **kwarg):
        okta_login = False
        if 'state' in kwarg and kwarg['state'] == 'okta_login':
            _logger.info("OKTA LOGIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            okta_login = True

        _logger.info("OKTA login data: %r" % kwarg)
        if okta_login:
            user = request.env['res.users'].sudo().login_office_user(
                kwarg.get('code'))
            if not user or len(user) > 1:
                return werkzeug.utils.redirect("/")
            request.session.rotate = True
            request.session.uid = user.id
            request.session.login = user.login
            request.session.session_token = user.id and \
                                            user._compute_session_token(
                                                request.session.sid)
            request.uid = user.id
            request.disable_db = False
            _logger.info('\'%s\' successfully logged in with Okta' % user.name)
        return werkzeug.utils.redirect("/")
