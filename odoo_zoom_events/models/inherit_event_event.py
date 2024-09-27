
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



class inheritEventZoom(models.Model):
    _inherit = ["event.event"]

    meeting_type = fields.Selection(selection_add=[('odoo_zoom_events', 'Zoom'),])
    
    
    def odoo_zoom_events_CLOSE(self):
        # pass
        for rec in self:
            temp_key = rec.temp_key

            headers = {
                    'content-type': "application/json",
                    'authorization': "Bearer " + temp_key
                    }

            server_url = self.env['ir.config_parameter'].sudo().get_param('base_event_online.zm_server_url')           

            if not (server_url):
                raise ValidationError(_("Please Configure Zoom Server Global Configuration"))

            url = server_url + "/meetings/"+ rec.meeting_id + "/status"
            payload = "{\"action\":\"end\"}"            
            response = requests.request("PUT", url, data=payload,headers= headers)
            print (response.status_code )
            print ('#>>>>>MOD>>>odoo_zoom_events_CLOSE>>>>>>>>>>>>>>>>>>>>SUCCESS>>>>>>>>>>>' )

            if response.status_code == 204:
                return True



    def button_done(self):
    
        if self.meeting_type == 'odoo_zoom_events':  
            self.odoo_zoom_events_CLOSE()

        self.is_meeting_active = False
        for registration_ids in self.registration_ids:
            registration_ids.is_active = False                  

        res = super(inheritEventZoom, self).button_done()
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # zoom event initialiations
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def zoom_call_initiate(self,url,key,payload,show_message):
        for rec in self:
            print("zoom-call-initiate")
            
            headers = {
                'content-type': "application/json",
                'authorization': "Bearer " + key
                }

            try:
                response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
                json_response = json.loads(response.text)

            except Exception as e:
                _logger.info('----Exception-------')
                _logger.info(e)  
                return False

            if response.status_code == 201:
                _logger.info('---valid response code-------')

                rec.sudo().write({
                    'public_url':json_response['join_url'],
                    'meeting_id':json_response['id'],
                    'moderator_url':json_response['start_url'],
                    'temp_key':key,
                    'is_published':True,
                    'is_meeting_active':True,
                })

                for registration_ids in rec.registration_ids:
                    registration_ids.is_active = True                
                return True
            else:
                if show_message:
                    raise ValidationError(_(ast.literal_eval(response.text)['message']))

                _logger.info('---invalid response code-------')
                _logger.info(response.status_code)  
                return False




    def initiate_from_user_conf(self,server_url,payload):
        for rec in self:

            user_e_mail = self.user_id.zoom_email
            key = self.user_id.zoom_secret_key


            if not (user_e_mail or key):
                return False

            url = server_url+ "/users/" + user_e_mail + "/meetings"
            show_message = False

            return self.zoom_call_initiate(url,key,payload,show_message)       

           




    def initiate_class(self):
        for rec in self:

            res = super(inheritEventZoom, self).initiate_class()

            if self.meeting_type == 'odoo_zoom_events':
                for rec in self:
                    server_url = self.env['ir.config_parameter'].sudo().get_param('base_event_online.zm_server_url')           


                    if not (server_url):
                        raise ValidationError(_("Please Configure Global Zoom Configuration"))           
                
                    if not rec.moderator_password:
                        raise ValidationError(_("Please Provide Moderator Password to initiate meeting"))           
                    
                    payload = {
                            "topic":rec.name,
                            "type":"1",
                            "password":rec.moderator_password,
                            "agenda":rec.name,
                            "recurrence":{"type":"2"},
                            "settings":{"approval_type":"2"}                    
                            }
            

                    call_end = self.initiate_from_user_conf(server_url,payload)

                    if call_end:
                        return True
                        
                    global_e_mail =self.env['ir.config_parameter'].sudo().get_param('base_event_online.e_mail')
                    global_zoom_key =self.env['ir.config_parameter'].sudo().get_param('base_event_online.zoom_secret_key')       

                    if not (global_e_mail):
                        raise ValidationError(_("Please Configure Global Zoom Authentication Parameters"))

                    if not (global_zoom_key):
                        raise ValidationError(_("Please Configure Global Zoom Authentication Parameters"))
                

                    url = server_url+ "/users/" + global_e_mail + "/meetings"
                    show_message = True

                    if not self.zoom_call_initiate(url,global_zoom_key,payload,show_message):
                        raise ValidationError(_("Zoom Meeting is not Initiated due to error in configuration"))



                

            

            return res
   



 
    


