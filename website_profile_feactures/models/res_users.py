import logging

from odoo import models, fields, api, _
from odoo.addons.auth_signup.models.res_partner import now
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


WRITEABLE_FIELDS = [
    'birthday', 'phone', 'sector', 'workplace', 'goals_first', 'goals_second','age',
    'goals_third', 'goals_financial_first', 'goals_financial_second',
    'goals_financial_third', 'street', 'state_id', 'website','user_only_name','user_last_name','town_id',
    'provincia','municipio','distritos_municipales','mobile', 'gender']

READABLE_FIELDS = [
    'birthday', 'sector', 'workplace', 'goals_first', 'goals_second','age',
    'goals_third', 'goals_financial_first', 'goals_financial_second',
    'goals_financial_third', 'street', 'state_id', 'website','user_only_name','user_last_name','town_id',
    'provincia','municipio','distritos_municipales','mobile', 'gender']


class Partner(models.Model):
    _inherit = 'res.partner'

    lastname = fields.Char(string="Apellido", )
    town_id = fields.Many2one(
        comodel_name="res.country.town",
        string="Municipio",
    )
    sector = fields.Char(
        string="Sector",
    )

    provincia = fields.Char(
        string="Provincia",
    )

    municipio = fields.Char(
        string="Municipio",
    )

    distritos_municipales = fields.Char(
        string="Distritos Municipales",
    )
    gender = fields.Selection(
        selection=[
            ('M', 'Hombre'),
            ('F', 'Mujer'),
            ('O', 'Otro'),
        ],
        string="Sexo",
        default="",
    )

    @api.model
    def signup_retrieve_info(self, token):
        res = super(Partner, self).signup_retrieve_info(token)
        res.update({
            'vat': self.vat,
            'lastname': self.lastname,
        })
        return res


class Users(models.Model):
    _inherit = 'res.users'

    lastname = fields.Char(string="Apellido", )
    birthday = fields.Date('Date of Birth')
    age = fields.Integer('Edad')
    sector = fields.Char(string='Sector')
    workplace = fields.Char(string='Work Place')
    goals_first = fields.Char(string='Goal #1')
    goals_second = fields.Char(string='Goal #2')
    goals_third = fields.Char(string='Goal #3')
    profile_percent = fields.Float(
        string='Profile percent',
        default=0.0,
    )
    goals_financial_first = fields.Char(string='Goal Finacial #1')
    goals_financial_second = fields.Char(string='Goal Finacial #2')
    goals_financial_third = fields.Char(string='Goal Finacial #3')
    town_id = fields.Many2one(
        comodel_name="res.country.town",
        string="Municipio",
    )
    gender = fields.Selection(
        selection=[
            ('M', 'Hombre'),
            ('F', 'Mujer'),
            ('O', 'Otro'),
        ],
        string="Sexo",
        default="",
    )

    def __init__(self, pool, cr):
        super(Users, self).__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(self.SELF_WRITEABLE_FIELDS + WRITEABLE_FIELDS))
        type(self).SELF_READABLE_FIELDS = type(
            self).SELF_READABLE_FIELDS + READABLE_FIELDS

