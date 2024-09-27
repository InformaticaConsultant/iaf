# -*- coding: utf-8 -*-
import logging
import string
import re
import requests

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


# class Document(models.Model):
#     _inherit = 'documents.document'
#
#     def access_content(self):
#         self.ensure_one()
#         action = {
#             'type': "ir.actions.act_url",
#             'target': "new",
#         }
#         if self.url:
#             action['url'] = self.url
#         elif self.type == 'binary':
#             action['url'] = '/documents/content/%s' % self.id
#         return action


class Folder(models.Model):
    _inherit = 'documents.folder'

    use_in_website = fields.Boolean(string="Use in website", )
    use_in_capsule = fields.Boolean(string="Usar en Capsulas", )


class Document(models.Model):
    _inherit = 'documents.document'

    use_in_capsule = fields.Boolean(related="folder_id.use_in_capsule", )
    use_in_home = fields.Boolean(string="Usar en el homepage", )
    main_video = fields.Boolean(string="Video principal", )
    author_name = fields.Char(string="Autor", )
    embed_code = fields.Char(string="Código incrustado", )
    description = fields.Text(string="Descripción", )

    @api.onchange('url')
    def _onchange_url(self):
        if self.url:
            if 'vimeo' in self.url:
                embed_code = '''
                <iframe src="%s" allowFullScreen="true" 
                    allow="autoplay; fullscreen; picture-in-picture" 
                    allowfullscreen="true" frameborder="0" id=%s/>'''

                if self.main_video:
                    id_selector = "main_video"
                else:
                    id_selector = "video_item"
                api_vimeo = "https://vimeo.com/api/oembed.json?url={}".format(
                    self.url)
                try:
                    data = requests.get(api_vimeo)
                    if data.status_code == 200:
                        data = data.json()
                        src = data.get('html').split(' ')[1]
                        link = src.replace('src="', '').replace('"', '')
                        self.update({
                            'name': data.get('title'),
                            'author_name': data.get('author_name'),
                            'description': data.get('description'),
                            'embed_code': link,
                            # 'embed_code': embed_code % (link, id_selector),
                        })
                except requests.exceptions.ConnectionError as e:
                    super(Document, self)._onchange_url()
        else:
            super(Document, self)._onchange_url()

    def capsulas(self):
        folder = self.env['documents.folder'].sudo().search([
            ('use_in_website', '=', True),
            ('use_in_capsule', '=', True),
            ('parent_folder_id', '=', False),
        ])

        values = {
            'folder_name': folder.name,
            'main_video': False,
            'documents': [],
        }
        # In home we only can show 4 videos
        count = 0
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

            if count == 4:
                break
            else:
                count += 1
        return values


class WebsiteGlosary(models.Model):
    _name = 'website.glosary'
    _description = 'Website glosary'

    def _get_letter(self):
        """ Return the alphabet in a list of tuple. """
        letters = list(string.ascii_uppercase)
        alphabet = [(letter, letter) for letter in letters]
        return alphabet

    name = fields.Char(string="Name", required=True, )
    letter = fields.Selection(
        selection="_get_letter",
        string="Letter",
        required=True,
    )
    definition = fields.Text(string="Definition", required=True, )

    def name_get(self):
        res = []
        for record in self:
            name = "[%s] %s" % (record.letter, record.name)
            res.append((record.id, name))
        return res
