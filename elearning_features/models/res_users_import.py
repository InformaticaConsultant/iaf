import base64
import csv
import logging
import io
import pandas

from odoo.tools.translate import _
from odoo.exceptions import UserError

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class ImportUser(models.Model):
    _name = 'import.user'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Import user'

    name = fields.Char(
        string="Empresa",
        required=True,
    )
    rnc = fields.Char(
        string="RNC",
        required=True,
    )
    email = fields.Char(
        string="Correo",
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Contacto",
        readonly=True,
        store=True,
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string="Usuarios",
        readonly=True,
    )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.name))
        return res

    def import_user(self):
        """Create users from attachment csv file """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User '
                              'Preferences to send emails.'))

        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'import.user'),
            ('res_id', '=', self.id),
        ])

        if len(attachment) > 1:
            attachment = attachment[0]

        partner = self.env['res.partner'].search([
            ('vat', '=', self.rnc.replace('-', ''))
        ])

        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.name,
                'vat': self.rnc,
                'email': self.email,
                'is_company': True,
            })

        # if attachment.mimetype != 'text/csv':
        #     raise UserError("El archivo suministrado no es un CSV.")
        new_users = []
        with io.BytesIO(base64.b64decode(attachment.datas)) as buffer:
            excel_data_df = pandas.read_excel(buffer, engine='xlrd')

            for item in excel_data_df.to_dict(orient='record'):
                name = item.get('NOMBRE').strip()
                lastname = item.get('APELLIDO').strip()
                cedula = str(item.get('CEDULA')).replace('-', '')
                email = item.get('CORREO')

                # Check if user with this email already exists
                user_exist = self.env['res.users'].search([
                    ('login', '=', email)
                ])
                if user_exist:
                    raise UserError("Ya existe un usuario con el correo: %s" %
                                    email)
                if not name or not lastname or not cedula or not email:
                    raise UserError("Favor revisar el archivo, faltan datos")

                partner = self.env['res.partner'].create({
                    'name': name,
                    'lastname': lastname,
                    'vat': cedula,
                    'email': email,
                    'parent_id': partner.id,
                    'company_id': self.env.company.id,
                })

                template_user = self.env.ref(
                    "base.template_portal_user_id")
                user_values = {
                    'name': name,
                    'lastname': lastname,
                    'login': email,
                    'partner_id': partner.id,
                    'company_id': self.env.company.id,
                    'groups_id': template_user.groups_id,
                    'active': True,
                }

                _logger.info("Creating user from file: %r" % user_values)
                user = self.env['res.users'].with_context(
                    no_reset_password=True).create(user_values)

                if user:
                    new_users.append(user.id)
                    template = self.env.ref(
                        'elearning_features.set_password_email',
                        raise_if_not_found=False)
                    template_values = {
                        'email_to': '${object.email|safe}',
                        'email_cc': False,
                        'auto_delete': True,
                        'partner_to': False,
                        'scheduled_date': False,
                    }

                    template.write(template_values)
                    template.with_context(lang=user.lang).send_mail(
                        user.id, force_send=True, raise_exception=True)
                    _logger.info(
                        "Password reset email sent for user <%s> to <%s>",
                        user.login, user.email)
        if new_users:
            self.write({'user_ids': [(6, 0, new_users)]})
        title = _("Importación exitosa!")
        message = "Se han creado %d nuevos usuarios. Les hemos enviado un " \
                  "correo de invitación" % len(new_users)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': False,
            }
        }
