# -*- coding: utf-8 -*-
import logging
import re

import werkzeug
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.web.controllers.main import ensure_db

import odoo
from odoo import http, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteEventControllerInherit(WebsiteEventController):
    @http.route(['''/event/<model("event.event", "[('website_id', 'in', (False, current_website_id))]"):event>/register'''], type='http', auth="public", website=True, sitemap=False)
    def event_register(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        current_partner = request.env['res.users'].search([('id','=',request.session.uid)]).partner_id
        user_registration = request.env['event.registration'].sudo().search([('event_id','=',event.id),('partner_id','=',current_partner.id)],order='id desc',limit=1)
        
        values = self._prepare_event_register_values(event, **post)
        values['user_registration_object'] = user_registration
        values['registrable'] = event.event_registrations_open
        return request.render("website_event.event_description_full", values)