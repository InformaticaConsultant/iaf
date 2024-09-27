from odoo import models, fields, api, _, http
from odoo.addons.http_routing.models.ir_http import slug


class WebsitePodcast(models.Model):
    _name = 'website.podcast'
    _description = 'Website Podcast'

    _rec_name = 'name'
    _order = 'sequence,name ASC'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    image = fields.Image(
        string='Image',
    )
    header_image = fields.Image(
        string='Header Image',
        required=True
    )
    website_published = fields.Boolean(
        string='Published on Website',
        default=False
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    duration = fields.Float(
        string='Duration',
        help='Format -> Hours:Minutes',
    )
    guest_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='website_podcast_res_partner_guest_rel',
        column1='res_partner_id',
        column2='website_podcast_id',
        string='Guests'
    )
    host_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='website_podcast_res_partner_host_rel',
        column1='res_partner_id',
        column2='website_podcast_id',
        string='Hosts'
    )
    website_url = fields.Char(
        string='Website Url',
        compute='_compute_website_url',
        help='The full URL to access the server action through the website.'
    )
    position = fields.Integer(
        string='Position',
        compute='_compute_position'
    )
    related_podcast_ids = fields.Many2many(
        string='Related Podcasts',
        comodel_name='website.podcast',
        relation='website_podcast_website_podcast1_rel',
        column1='website_podcast_id',
        column2='website_podcast1_id',
    )
    spotify_url = fields.Char(
        string='Spotify Url',
        help='Add complete url from Spotify',
    )
    google_url = fields.Char(
        string='Google Url',
        help='Add complete url from Google podcast',
    )
    apple_podcast_url = fields.Char(
        string='Apple podcast Url',
        help='Add complete url from Apple podcast',
    )
    youtube_url = fields.Char(
        string='Youtube Url',
        help='Add complete url from Youtube',
    )
    category_id = fields.Many2one(
        string='Category',
        comodel_name='website.podcast.category',
    )
    guest_count = fields.Integer(
        string='Guest Count',
        compute='_compute_guest_count',
    )
    host_count = fields.Integer(
        string='Host Count',
        compute='_compute_host_count',
    )

    def _compute_guest_count(self):
        for podcast in self:
            podcast.guest_count = len(podcast.guest_ids)

    def _compute_host_count(self):
        for podcast in self:
            podcast.host_count = len(podcast.host_ids)

    def _compute_position(self):
        for podcast in self:
            podcasts = self.env['website.podcast'].search([])
            podcast.position = podcasts.ids.index(podcast.id) + 1

    def _compute_website_url(self):
        for podcast in self:
            podcast.website_url = "/podcasts/%s/" % slug(podcast)

    def open_website_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
        }
    
    def get_pagination_related_podcast(self, page_size):
        self.ensure_one()
        pages = []
        def paginate(data, page_size, page_number):
            start = (page_number - 1) * page_size
            end = start + page_size
            return data[start:end]
        
        page_number = 1

        while True:
            page = paginate(self.related_podcast_ids, page_size, page_number)
            if not page:
                break
            pages.append(page)
            page_number += 1

        return pages
    
class WebsitePodcastCategory(models.Model):
    _name = 'website.podcast.category'
    _description = 'Website Podcast Category'
    
    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
    )
    podcast_ids = fields.One2many(
        string='Podcasts',
        comodel_name='website.podcast',
        inverse_name='category_id',
    )
    podcast_count = fields.Integer(
        string='Podcast Count',
        compute='_compute_podcast_count',
    )

    def _compute_podcast_count(self):
        for category in self:
            category.podcast_count = len(category.podcast_ids)
