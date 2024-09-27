# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
import base64
import logging
import hashlib
import uuid
import werkzeug
from werkzeug import urls
from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import ustr
from odoo.modules.module import get_module_resource
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now

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


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('elearning_features', 'static/src/img',
                                         'user_profile.png')
        _logger.info("Image user default: %r" % image_path)
        return base64.b64encode(open(image_path, 'rb').read())

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
    goals_financial_first = fields.Char(string='Goal Finacial #1')
    is_account_confirmed = fields.Boolean(default=False, )
    image_1920 = fields.Image(default=_default_image)
    user_type = fields.Selection(
        selection=[
            ('younger', 'Menor de edad'),
            ('adult', 'Mujer'),
            ('foreign', 'Extranjero'),
        ],
        string="Estatus legal",
        default="younger",
    )
    user_status = fields.Boolean(string="Estado estatus legal", )
    complete_name = fields.Char(
        string="Nombre",
        compute="_compute_name",
    )

    forum_waiting_posts_count = fields.Integer('Waiting post', compute="_get_user_waiting_post")

    def _get_user_waiting_post(self):
        for user in self:
            Post = self.env['forum.post']
            domain = [('parent_id', '=', False), ('state', '=', 'pending'), ('create_uid', '=', user.id)]
            user.forum_waiting_posts_count = Post.search_count(domain)

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + WRITEABLE_FIELDS

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + READABLE_FIELDS

    # Se reemplaza por las propiedades SELF_WRITEABLE_FIELDS, SELF_READABLE_FIELDS
    # def __init__(self, *args, **kwargs):
    #     super(Users, self).__init__(*args, **kwargs)
    #     type(self).SELF_WRITEABLE_FIELDS = list(
    #         set(self.SELF_WRITEABLE_FIELDS + WRITEABLE_FIELDS))
    #     type(self).SELF_READABLE_FIELDS = type(
    #         self).SELF_READABLE_FIELDS + READABLE_FIELDS

    def _compute_name(self):
        for user in self:
            partner = user.partner_id
            user.complete_name = "%s %s" % (partner.name,
                                            partner.lastname or '')

    def name_get(self):

        res = []
        for record in self:
            res.append((record.id, "%s %s" % (record.name, record.partner_id.lastname or '')))

        return res

    def _assign_image(self):
        image_path = get_module_resource('elearning_features',
                                         'static/src/img',
                                         'user_profile.png')
        user_image = base64.b64encode(open(image_path, 'rb').read())
        for user in self:
            user.write({'image_1920': user_image})
            user.partner_id.write({'image_1920': user_image})
        return True

    @api.model
    def create(self, values):
        """ Trigger automatic subscription based on user groups """
        image_path = get_module_resource('elearning_features',
                                         'static/src/img',
                                         'user_profile.png')
        user_image = base64.b64encode(open(image_path, 'rb').read())
        values['image_1920'] = user_image
        user = super(Users, self).create(values)
        if user.has_group('base.group_user'):
            user.update({'is_account_confirmed': True})
        user.partner_id.write({'image_1920': user_image})
        return user

    @api.model
    def _generate_token(self, user_id, email):
        """Return a token for email validation. This token is valid for the day
        and is a hash based on a (secret) uuid generated by the forum module,
        the user_id, the email and currently the day (to be updated if
        necessary).
        """
        profile_uuid = self.env['ir.config_parameter'].sudo().get_param(
            'website_profile.uuid')
        if not profile_uuid:
            profile_uuid = str(uuid.uuid4())
            self.env['ir.config_parameter'].sudo().set_param(
                'website_profile.uuid', profile_uuid)
        return hashlib.sha256((u'%s-%s-%s-%s' % (
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            profile_uuid,
            user_id,
            email
        )).encode('utf-8')).hexdigest()

    def _send_account_validation_email(self, **kwargs):
        if not self.email:
            return False
        template = self.env.ref('elearning_features.account_validation_email')
        if template:
            token = self._generate_token(self.id, self.email)
            params = {
                'token': token,
                'user_id': self.id,
                'email': self.email,
            }
            params.update(kwargs)
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            token_url = '%s/account/validate_email?%s' % (base_url,
                urls.url_encode(params))

            email_from = "Academia Finanzas con Propósito Popular <%s>"
            company_email = self.env.user.company_id.email
            with self._cr.savepoint():
                template.sudo().with_context(
                    token_url=token_url).send_mail(
                    self.id,
                    force_send=True,
                    raise_exception=False,
                    email_values={
                        'email_to': self.email,
                        "email_from": email_from % company_email,
                    }
                )
        return True

    def _process_account_validation_token(self, user_id, token, email):
        self.ensure_one()
        validation_token = self._generate_token(user_id, email)
        if token == validation_token and self.karma == 0:
            return True

        return False

    def _rank_changed(self):
        """
            Method that can be called on a batch of users with the same new rank
        """
        # template = self.env.ref(
        #     'elearning_features.mail_template_data_new_rank_reached',
        #     raise_if_not_found=False)
        # if template:
        #     for u in self:
        #         if u.rank_id.karma_min > 0:
        #             template.send_mail(
        #                 u.id,
        #                 force_send=len(self) == 1,
        #                 notif_layout='mail.mail_notification_light')
        return True

    def get_gamification_redirection_data(self):
        res = super(Users, self).get_gamification_redirection_data()
        for item in res:
            if item.get('url') == '/slides':
                item['label'] = 'Conoce nuestro eLearning'
            elif item.get('url') == '/cursos':
                item['label'] = 'Conoce nuestro eLearning'
            elif item.get('url') == '/forum':
                item['label'] = 'Nuestros foros'

        return res

    def action_reset_password(self):
        """ create signup token for each user, and send their signup
        url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(
            signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref(
                    'elearning_features.set_password_email',
                    raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('elearning_features.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.email:
                raise UserError(_(
                    "Cannot send email: user %s has no email address.") %
                                user.name)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.with_context(lang=user.lang).send_mail(
                    user.id, force_send=force_send, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>",
                         user.login, user.email)

    def send_unregistered_user_reminder(self, after_days=5):
        datetime_min = fields.Datetime.today() - relativedelta(days=after_days)
        datetime_max = datetime_min + relativedelta(hours=23, minutes=59, seconds=59)

        res_users_with_details = self.env['res.users'].search_read([
            ('share', '=', False),
            ('create_uid.email', '!=', False),
            ('create_date', '>=', datetime_min),
            ('create_date', '<=', datetime_max),
            ('log_ids', '=', False)], ['create_uid', 'name', 'login'])

        # group by invited by
        invited_users = defaultdict(list)
        for user in res_users_with_details:
            invited_users[user.get('create_uid')[0]].append("%s (%s)" % (user.get('name'), user.get('login')))

        mail_template = "mail_template_data_unregistered_users"
        # For sending mail to all the invitors about their invited users
        for user in invited_users:
            template = self.env.ref(
                'elearning_features.%s' % mail_template).with_context(
                dbname=self._cr.dbname, invited_users=invited_users[user])
            template.send_mail(user,
                               notif_layout='mail.mail_notification_light',
                               force_send=False)
