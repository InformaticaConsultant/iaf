from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ftp_url = fields.Char(string='FTP Url')
    ftp_login = fields.Char(string='FTP Login', )
    ftp_password = fields.Char(string='FTP Password', )

    def get_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res.update(ftp_url=ICP.get_param('elearning_features.ftp_url'))
        res.update(ftp_url=ICP.get_param('elearning_features.ftp_login'))
        res.update(ftp_url=ICP.get_param('elearning_features.ftp_password'))

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('elearning_features.ftp_url', self.ftp_url)
        ICP.set_param('elearning_features.ftp_login', self.ftp_login)
        ICP.set_param('elearning_features.ftp_password', self.ftp_password)
