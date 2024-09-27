
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import json


class BlogPost(models.Model):
    _inherit = "blog.post"

    short_description = fields.Char(
        string="Descripción corta",
        size=160,
    )

    def get_image_path(self):

        path_img = ""

        for record in self:
            data = json.loads(record.cover_properties)
            path_img = data.get('background-image')
            path_img = path_img.replace('(','').replace(')','').replace('\'','').replace('url','')


        if not path_img or path_img =='none':
            path_img= "/elearning_features/static/src/img/blog/portada3.jpg"
    
        return  path_img