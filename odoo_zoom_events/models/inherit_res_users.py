
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import fields, models


class InheritResUsersZoom(models.Model):
    _inherit = 'res.users'

   
    show_zoom_settings = fields.Boolean(default=True,store=True)   
     
   
   
   