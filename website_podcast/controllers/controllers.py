# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import math

class PodcastController(http.Controller):

    @http.route('/podcasts', type='http', auth="public", website=True)
    def list_podcasts(self, **kw):
        podcasts = request.env['website.podcast'].sudo().search([
            ('active', '=', True), 
            ('website_published', '=', True),
        ], limit=8, offset=0)

        return request.render('website_podcast.website_podcasts_template', {
            'podcasts': podcasts,
        })

    @http.route(['/podcasts/<model("website.podcast"):podcast>'], type='http', auth="public", website=True)
    def podcast(self, podcast, **kw):
        sudo_podcasts = podcast.sudo()
        return request.render('website_podcast.website_podcast_template', {
            'podcast': sudo_podcasts,
            'main_object': sudo_podcasts
        })

    @http.route(['/podcast/search'], type='json', auth="public", website=True)
    def podcast_search(self, search_term=None, search_type='podcast', offset=0, limit=8, **kwargs):
        domain = [
            ('active', '=', True), 
            ('website_published', '=', True)
        ]

        if search_term:
            if search_type == 'name':
                domain = [('name', 'ilike', search_term)]
            elif search_type == 'host':
                domain = [('host_ids.name', 'ilike', search_term)]

        podcasts = request.env['website.podcast'].sudo().search(domain, limit=limit, offset=offset)

        return [
            request.env['ir.ui.view']._render_template('website_podcast.website_podcast_list', {'podcasts': podcasts}),
            len(podcasts)
        ]