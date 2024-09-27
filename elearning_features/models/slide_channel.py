# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}


class SlideTeacherFollower(models.Model):
    _name = 'slide.teacher.follower'
    _description = 'Teacher followers'

    name = fields.Char(string="Name", )
    channel_id = fields.Many2one(
        comodel_name='slide.channel',
        index=True,
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        index=True,
        required=True,
    )
    partner_email = fields.Char(related='partner_id.email', readonly=True, )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.name))
        return res

    @api.model
    def create(self, vals):
        channel = self.env['slide.channel'].browse(vals.get('channel_id'))
        vals['name'] = "%s-%s" % (channel.name, channel.user_id.partner_id.name)
        follower = super(SlideTeacherFollower, self).create(vals)
        return follower


class SuggestBankProduct(models.Model):
    _name = 'suggest.bank.product'
    _description = 'Suggest bank product'

    name = fields.Char(string="Name", )
    description = fields.Text(string="Description", )
    benefit = fields.Char(string="Benefit", )
    url = fields.Char(string="URL", )
    active = fields.Boolean(default=True)
    channel_ids = fields.Many2many(comodel_name='slide.channel', )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.name))
        return res

    def get_text_from_html(self):
        soup = BeautifulSoup(self.description, 'lxml')
        return soup.text


class Channel(models.Model):
    _inherit = 'slide.channel'

    partner_id = fields.Many2one(
        related="user_id.partner_id",
    )
    partner_name = fields.Char(
        string="Partner Name",
        related="partner_id.name",
    )
    publish_template_id = fields.Many2one(
        'mail.template', string='Correo de nuevo contenido',
        help="Email template to send slide publication through email",
        # default=lambda self: self.env['ir.model.data'].xmlid_to_res_id(
        #     'elearning_features.slide_template_published'))
        default=lambda self: self.env.ref(
            'elearning_features.slide_template_published').id)

    def default_slide_template_share(self):
        record_template =  self.env.ref(
            'elearning_features.slide_template_shared', False)
        if record_template:
            return record_template.id
        return False

    share_template_id = fields.Many2one(
        'mail.template', string='Plantilla contenido compartido',
        help="Email template used when sharing a slide",
        # default=lambda self: self.env['ir.model.data'].xmlid_to_res_id(
        #     'elearning_features.slide_template_shared'))
        default= default_slide_template_share)

    is_teacher_follower = fields.Boolean(string='Is teacher follower')
    suggest_bank_product_ids = fields.Many2many(
        comodel_name='suggest.bank.product',
        relation='rel_channel_suggest_product',
        column1='channel_id',
        column2='suggest_product_id',
        string='Suggest products',
    )
    channel_with_limit_date = fields.Boolean(
        string='Asignar tiempo limite para completar el curso?')
    start_date = fields.Date(string='Fecha de inicio')
    interval_number = fields.Integer(default=1, help="Numero de  x.")
    segment = fields.Char(string='Segmento')
    short_description_slide = fields.Text(string='Descripcion Corta')
    date_for_publish = fields.Date(string='Fecha disponible',help="Fecha para indicarles a los visitante cuaando se publico el curso")
    interval_type = fields.Selection(
        selection=[
            ('days', 'Dias'),
            ('weeks', 'Semanas'),
            ('months', 'Meses'),
        ],
        string='Unidad de intervalos',
        default='months',
    )
    mail_sended = fields.Boolean(default=False)
    survey_tag_ids = fields.Many2many(
        comodel_name='slide.channel.tag',
        relation='survey_slide_channel_tag_rel',
        column1='channel_id',
        column2='tag_id',
        string='Etiquetas de encuesta',
    )

    # def _compute_slide_partner_info(self):
    #     current_user_info = self.env['slide.channel'].sudo().search(
    #         [('channel_id', 'in', self.ids),
    #          ('partner_id', '=', self.env.user.partner_id.id)]
    #     )
    #
    #     for slide in self:
    #         completed, completion = mapped_data.get(record.id, (False, 0))
    #         record.completed = completed
    #         record.completion = round(
    #             100.0 * completion / (record.total_slides or 1))

    @api.depends('name', 'website_id.domain')
    def _compute_website_url(self):
        super(Channel, self)._compute_website_url()
        for channel in self:
            # avoid to perform a slug on a not yet saved record in case of
            # an onchange.
            if channel.id:
                base_url = channel.get_base_url()
                channel.website_url = '%s/cursos/%s' % (base_url, slug(channel))

    def button_publish(self):
        for channel in self:
            for slide in channel.slide_ids.filtered(
                    lambda s: not s.website_published):
                slide.write({'website_published': True})

            values = {'website_published': True, 'mail_sended': True}
            # channel.write({'website_published': True, 'mail_sended': True})

            if not channel.product_id:
                product = channel.env['product.product'].search([
                    ('name', '=', self.name)
                ])
                if not product:
                    product = channel.env['product.product'].create({
                        'name': self.name,
                        'type': 'service',
                        'categ_id': self.env.ref('product.product_category_all').id,
                        'taxes_id': [(6, self.env.ref('l10n_do.1_tax_0_sale').id)],
                        'purchase_ok': False,
                        'invoice_policy': 'order',
                        'active': True,
                        'website_published': True,
                    })
                values['product_id'] = product.id

            channel.write(values)

    def action_channel_invite(self):
        self.ensure_one()
        template = self.env.ref(
            'elearning_features.mail_template_slide_channel_invite',
            raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_channel_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            notif_layout='mail.mail_notification_light',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'slide.channel.invite',
            'target': 'new',
            'context': local_context,
        }

    def send_email_new_course(self):
        # portal_group = self.env.ref('base.group_portal')
        # emails = []
        # for user in portal_group.users:
        #     emails.append(user.login.strip())
        #
        # mail_template = self.env.ref(
        #     'elearning_features.email_template_new_course',
        #     raise_if_not_found=False)
        #
        # for channel in self.filtered(lambda c: c.is_published):
        #     for email in emails:
        #         mail_template.send_mail(
        #             channel.id, force_send=True, email_values={
        #                 'email_to': email,
        #             })
        return True

    def send_email_add_members(self):
        for channel in self:
            template = self.env.ref(
                'elearning_features.email_template_add_member_slide_elearning',
                raise_if_not_found=False)
            template.sudo().send_mail(channel.id)

    def send_email_remove_members(self):
        for channel in self:
            template = self.env.ref(
                'elearning_features.email_template_remove_member_slide_elearning',
                raise_if_not_found=False)
            template.sudo().send_mail(channel.id)

    def _action_add_members(self, target_partners, **member_values):
        result = super(Channel, self)._action_add_members(
            target_partners, **member_values)
        if result:
            self.sudo().send_email_add_members()

        for slide_partner in result:
            channel = slide_partner.channel_id
            if channel.channel_with_limit_date and channel.interval_type and \
                    channel.interval_number > 0 and result:
                timezone = self._context.get('tz') or \
                           self.env.user.partner_id.tz or 'UTC'

                # convert date and time into user timezone
                self_tz = self.with_context(tz=timezone)

                now = fields.Datetime.context_timestamp(
                    self_tz, datetime.datetime.now())
                # fields.Datetime.context_timestamp(event, event.date_begin)
                nextcall = now + _intervalTypes[channel.interval_type](
                    channel.interval_number)
                slide_partner.write({'limit_date': nextcall.date()})

        return result

    def _remove_membership(self, partner_ids):
        super(Channel, self)._remove_membership(partner_ids)
        self.sudo().send_email_remove_members()

    def unlink(self):
        for channel in self:
            channel.slide_ids.unlink()
            if channel.product_id:
                channel.product_id.write({'active': False})
            if channel.suggest_bank_product_ids:
                channel.write({'suggest_bank_product_ids': [(5, 0, 0)]})
            if channel.channel_partner_ids:
                channel.channel_partner_ids.unlink()
        return super(Channel, self).unlink()
        

class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'
    
    limit_date = fields.Date('Limite para completar el curso')
    started = fields.Boolean('Curso iniciado')
    email_sended = fields.Boolean('Email enviado')

    def send_email_reminder_end_the_course(self):
        template = self.env.ref(
            'elearning_features.email_template_limit_date_reminder_member_'
            'slide_elearning', raise_if_not_found=False)
        template.sudo().send_mail(self.id)

    def check_limit_date(self):
        for slide in self:
            if slide.limit_date:
                date = slide.limit_date
                actual_date = datetime.date.today()
                days_for_expiration = (date - actual_date).days
                if days_for_expiration < 3:
                    self.send_email_reminder_end_the_course()
                if days_for_expiration <=0:
                    return False
        return True

    def check_slide_channel_partner(self):
        records = self.search([('limit_date', '!=', False)])
        for record in records:
            if record.check_limit_date():
                channel = self.env['slide.channel'].browse(record.channel_id.id)
                channel._remove_membership(record.partner_id.ids)

    def _recompute_completion(self):
        super(SlideChannelPartner, self)._recompute_completion()
        for record in self.filtered(lambda e: not e.email_sended and e.member_status=='completed'):
            record.send_email_course_complete()
            record.email_sended = True

    def send_email_course_complete(self):
        template = self.env.ref(
            'elearning_features.email_template_course_completed',
            raise_if_not_found=False)

        for cp in self.filtered(lambda c: c.completed and not c.email_sended):
            email_from = "Academia Finanzas con Propósito Popular <%s>"
            template.send_mail(
                self.id, force_send=True, email_values={
                    'email_to': cp.partner_email.strip(),
                    "email_from": email_from % self.env.user.company_id.email,
                })
        return True


class Survey(models.Model):
    _inherit = 'survey.survey'

    academy_survey = fields.Boolean(string='Encuesta Academia?')
    