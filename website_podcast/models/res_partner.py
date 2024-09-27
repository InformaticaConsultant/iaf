from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    youtube = fields.Char(
        string='Youtube@',
        help='Just add the social media name (not the full link).'
    )
    facebook = fields.Char(
        string='Facebook@',
        help='Just add the social media name (not the full link).'
    )
    twitter = fields.Char(
        string='Twitter@',
        help='Just add the social media name (not the full link).'
    )
    instagram = fields.Char(
        string='Instagram@',
        help='Just add the social media name (not the full link).'
    )
    linkedin = fields.Char(
        string='Linkedin@',
        help='Just add the social media name (not the full link).'
    )
    podcast_host_ids = fields.Many2many(
        string='Podcasts hosted',
        comodel_name='website.podcast',
        relation='website_podcast_res_partner_host_rel',
        column1='website_podcast_id',
        column2='res_partner_id',
    )
    podcast_guest_ids = fields.Many2many(
        string='Podcasts guest',
        comodel_name='website.podcast',
        relation='website_podcast_res_partner_guest_rel',
        column1='website_podcast_id',
        column2='res_partner_id',
    )
    