
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################



from odoo import fields, models

class ResConfigInheritZoomEvent(models.TransientModel):
    _inherit = 'res.config.settings'
 

    
    zm_server_url = fields.Char(string='Zoom Server Url')    
    e_mail = fields.Char(string='E Mail',)
    zoom_secret_key = fields.Char(string='jWT Token',)     

    bb_server_url = fields.Char(string='Server Url')
    bb_secret_key = fields.Char(string='Authentication Secret',)




    def get_values(self):
        res = super(ResConfigInheritZoomEvent, self).get_values()
        res.update(zm_server_url=self.env['ir.config_parameter'].sudo().get_param('base_event_online.zm_server_url'))
        res.update(e_mail=self.env['ir.config_parameter'].sudo().get_param('base_event_online.e_mail'))
        res.update(zoom_secret_key=self.env['ir.config_parameter'].sudo().get_param('base_event_online.zoom_secret_key'))

        res.update(bb_server_url=self.env['ir.config_parameter'].sudo().get_param('base_event_online.bb_server_url'))
        res.update(bb_secret_key=self.env['ir.config_parameter'].sudo().get_param('base_event_online.bb_secret_key'))


        return res

    def set_values(self):
        super(ResConfigInheritZoomEvent, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('base_event_online.zm_server_url', self.zm_server_url)
        self.env['ir.config_parameter'].sudo().set_param('base_event_online.e_mail', self.e_mail)
        self.env['ir.config_parameter'].sudo().set_param('base_event_online.zoom_secret_key', self.zoom_secret_key)


        self.env['ir.config_parameter'].sudo().set_param('base_event_online.bb_server_url', self.bb_server_url)
        self.env['ir.config_parameter'].sudo().set_param('base_event_online.bb_secret_key', self.bb_secret_key)



