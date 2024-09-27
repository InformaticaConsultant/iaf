
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################



from odoo import models, fields, api
import requests
import json
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_is_zero
import ast
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class inheritEventRegistrtion(models.Model):
    _inherit = ["event.registration"]
    
    is_active = fields.Boolean(
        string='Active',        
        default=False,
        required=True,
        store=True 
    )
    
    is_moderator = fields.Boolean(
        string='is_moderator',        
        compute = "_compute_is_moderator"    
    )

    partner_id = fields.Many2one(
        'res.partner', string='Contact')

    
    @api.depends("event_id")
    def _compute_is_moderator(self):
        print('_compute_is_moderator')
        for rec in self:
            if rec.env.user == rec.event_id.user_id:
                rec.is_moderator = True
            else:
                rec.is_moderator = False
            print('rec.is_moderator -- ', rec.is_moderator)
    

    def return_to_class(self):
        for rec in self:  
            if rec.meeting_id:
                return {
                    "type": "ir.actions.act_url",
                    "url": rec.compute_url,
                    "target": "new",
                }

    compute_url = fields.Char(string="Join Url",compute = "_compute_compute_url")
    meeting_id = fields.Char(string="Meeting Id",compute = "_compute_compute_url")
    compute_url_moderator = fields.Char(string="Moderator Url",compute = "_compute_compute_url")

    @api.depends("event_id")
    def _compute_compute_url(self):
        for rec in self:
            rec.meeting_id = rec.event_id.meeting_id

            compute_url = "Null"
            compute_url_moderator = "Null"

            rec.sudo().write({
                'compute_url':compute_url,
                'compute_url_moderator':compute_url_moderator
            })

