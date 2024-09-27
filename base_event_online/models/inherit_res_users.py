
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import fields, models


class InheritResUsers(models.Model):
    _inherit = 'res.users'

   
    show_zoom_settings = fields.Boolean(default=False,store=True)   
     
    zoom_email = fields.Char(string='E-Mail')
    zoom_secret_key = fields.Char(string='Zoom App(jWT) Token')

   
   