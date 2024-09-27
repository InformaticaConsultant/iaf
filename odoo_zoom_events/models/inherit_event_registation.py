
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
# import ast
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class inheritEventRegistrtion(models.Model):
    _inherit = ["event.registration"]
    
  
  

    def _compute_compute_url(self):
        res = super(inheritEventRegistrtion, self)._compute_compute_url()
        print (">>>>>>>>>>>>>>zoom _compute_compute_url")
          
        if self.is_active:
            self.meeting_id = self.event_id.meeting_id
            if self.meeting_id != "Null":
                if self.event_id.meeting_type =='odoo_zoom_events':
                    compute_url = self.event_id.public_url
                    compute_url_moderator = self.event_id.moderator_url
                
                    self.sudo().write({
                        'compute_url':compute_url,
                        'compute_url_moderator':compute_url_moderator
                    })
            

