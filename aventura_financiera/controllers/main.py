# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class WebsiteAventura(http.Controller):

    @http.route(['/aventura'], type='http', auth="public", website=True, sitemap=True)
    def aventura(self, **kwargs):
        return request.render("aventura_financiera.page_aventura")






