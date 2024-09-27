# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import calendar

from odoo import fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError


class Survey(models.Model):
    _inherit = 'survey.survey'

    def get_channel_url(self):
        slide = self.env['slide.slide'].search([
            ('survey_id', '=', self.id),
        ])
        return slide.channel_id.website_url

    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey
        message """
        # Ensure that this survey has at least one question.
        if not self.question_ids:
            raise UserError(
                _('You cannot send an invitation for a survey that has '
                  'no questions.'))

        # Ensure that this survey has at least one section with question(s),
        # if question layout is 'One page per section'.
        if self.questions_layout == 'page_per_section':
            if not self.page_ids:
                raise UserError(
                    _('You cannot send an invitation for a "One page per '
                      'section" survey if the survey has no sections.'))
            if not self.page_ids.mapped('question_ids'):
                raise UserError(
                    _('You cannot send an invitation for a "One page per '
                      'section" survey if the survey only contains empty '
                      'sections.'))

        if self.state == 'closed':
            raise UserError(
                _("You cannot send invitations for closed surveys."))

        template = self.env.ref(
            'elearning_features.mail_template_user_input_invite',
            raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_survey_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            notif_layout='mail.mail_notification_light',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    def _check_for_failed_attempt(self):
        """ If the user fails his last attempt at a course certification,
        we remove him from the members of the course (and he has to enroll again).
        He receives an email in the process notifying him of his failure and suggesting
        he enrolls to the course again.

        The purpose is to have a 'certification flow' where the user can re-purchase the
        certification when they have failed it."""

        if self:
            user_inputs = self.search([
                ('id', 'in', self.ids),
                ('state', '=', 'done'),
                ('quizz_passed', '=', False),
                ('slide_partner_id', '!=', False)
            ])

            if user_inputs:
                removed_memberships_per_partner = {}
                for user_input in user_inputs:
                    if user_input.survey_id._has_attempts_left(
                            user_input.partner_id, user_input.email,
                            user_input.invite_token):
                        # skip if user still has attempts left
                        continue
                    template = "mail_template_user_input_certification_failed"
                    self.env.ref('elearning_features.%s' % template).send_mail(
                        user_input.id,
                        notif_layout="mail.mail_notification_light"
                    )

                    removed_memberships = removed_memberships_per_partner.get(
                        user_input.partner_id,
                        self.env['slide.channel']
                    )
                    removed_memberships |= \
                        user_input.slide_partner_id.channel_id
                    removed_memberships_per_partner[user_input.partner_id] = \
                        removed_memberships

                dict_items = removed_memberships_per_partner.items()
                for partner_id, removed_memberships in dict_items:
                    removed_memberships._remove_membership(partner_id.ids)

    def get_date_formatted(self):
        month_name_dict = {
            'January': 'Enero',
            'February': 'Febrero',
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'October': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre',
        }

        month = calendar.month_name[fields.Date.today().month]
        month_name = month_name_dict[month]
        return {
            'day': fields.Date.today().day,
            'month': month_name.upper(),
            'year': fields.Date.today().year,
        }

    def get_channel(self):
        slide = self.env['slide.slide'].search([
            ('survey_id', '=', self.survey_id.id),
        ])
        return slide.channel_id.name

    def get_channel_url(self):
        slide = self.env['slide.slide'].search([
            ('survey_id', '=', self.survey_id.id),
        ])
        return slide.channel_id.website_url
