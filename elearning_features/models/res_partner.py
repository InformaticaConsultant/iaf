import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.elearning_features.controllers.main import \
    bpd_authenticate_cedula

_logger = logging.getLogger(__name__)


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
    is_teacher = fields.Boolean(string="Es un docente")
    short_description_teacher = fields.Text(string='Descripcion corta facilitador')
    long_description_teacher = fields.Text(string='Descripcion larga facilitador')
    social_twitter = fields.Char('Twitter Account')
    social_facebook = fields.Char('Facebook Account')
    social_github = fields.Char('GitHub Account')
    social_linkedin = fields.Char('LinkedIn Account')
    social_youtube = fields.Char('Youtube Account')
    social_instagram = fields.Char('Instagram Account')
    profile_html = fields.Text(string='Perfil profesional')
    user_type = fields.Selection(
        selection=[
            ('younger', 'Menor de edad'),
            ('adult', 'Mujer'),
            ('foreign', 'Extranjero'),
        ],
        string="Estatus legal",
        default="younger",
    )
    login_status = fields.Selection(
        selection=[
            ('valid', 'Válido'),
            ('invalid', 'Inválido'),
        ],
        string="Validación",
        default="",
    )
    user_status = fields.Boolean(string="Estado estatus legal", )
    complete_name = fields.Char(
        string="Nombre",
        compute="_compute_full_name",
    )

    @api.model
    def signup_retrieve_info(self, token):
        res = super(Partner, self).signup_retrieve_info(token)
        res.update({
            'vat': self.vat,
            'lastname': self.lastname,
        })
        return res

    def _compute_full_name(self):
        for partner in self:
            partner.complete_name = "%s %s" % (
                partner.name, partner.lastname or '')
            if not partner.login_status:
                bpd_api_instance = request.env['ir.config_parameter'].sudo(
                ).get_param('bpd.api')
                if not qcontext.get('token') and not qcontext.get(
                        'signup_enabled'):
                    raise werkzeug.exceptions.NotFound()
                valid_identification = True
                login_status = 'valid'
                if kw.get('cedula'):
                    cedula = kw.get('cedula').replace('-', '')
                    if bpd_api_instance and kw.get('user_type') == 'adult':
                        rstl = bpd_authenticate_cedula(cedula, bpd_api_instance)
                        is_valid = rstl.get('result')
                        if not is_valid:
                            valid_identification = False
                            login_status = 'invalid'
                res = bpd_authenticate_cedula()

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without
        re-browse the partner """
        partner = self
        name = "%s %s" % (partner.name or '', partner.lastname or '')

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[
                    partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name

    def get_my_user(self):
        for record in self:
            user = record.env['res.users'].sudo().search([
                        ('partner_id', '=', record.id)])

            return user
