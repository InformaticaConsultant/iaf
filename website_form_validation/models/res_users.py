import logging

from odoo import models, fields, api, _
from odoo.addons.auth_signup.models.res_partner import now
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    user_only_name = fields.Char(string='Solo Nombre del Usuario')
    user_last_name = fields.Char(string='Apellido de Usuario')
