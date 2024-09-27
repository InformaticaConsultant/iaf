
# -*- coding: utf-8 -*-
import base64
import datetime
import io
import logging
import re
import requests
import PyPDF2

from PIL import Image
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for

_logger = logging.getLogger(__name__)


class Slide(models.Model):
    _inherit = 'slide.slide'

    slide_required = fields.Boolean(string='Obligatorio')
    final_exam = fields.Boolean(string='Es un examen final')

    @api.onchange('datas')
    def _on_change_datas(self):
        """ For PDFs, we assume that it takes 5 minutes to read a page. """
        if self.datas:
            data = base64.b64decode(self.datas)
            if data.startswith(b'%PDF-'):
                pdf = PyPDF2.PdfFileReader(io.BytesIO(data),
                                           overwriteWarnings=False,
                                           strict=False)
                self.completion_time = (5 * len(pdf.pages)) / 60
                self.mime_type = 'application/pdf'
                if self.name:
                    self.name += '.pdf'
                else:
                    self.name = '.pdf'

    @api.depends('name', 'channel_id.website_id.domain')
    def _compute_website_url(self):
        # TDE FIXME: clena this link.tracker strange stuff
        super(Slide, self)._compute_website_url()
        for slide in self:
            if slide.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                base_url = slide.channel_id.get_base_url()
                # link_tracker is not in dependencies, so use it to shorten url only if installed.
                if self.env.registry.get('link.tracker'):
                    url = self.env['link.tracker'].sudo().create({
                        'url': '%s/cursos/curso/%s' % (base_url, slug(slide)),
                        'title': slide.name,
                    }).short_url
                else:
                    url = '%s/cursos/curso/%s' % (base_url, slug(slide))
                slide.website_url = url

    def get_channel_progress(self, channel, include_quiz=False):
        """ Replacement to user_progress. Both may exist in some transient state. """
        slides = self.env['slide.slide'].sudo().search([('channel_id', '=', channel.id)])
        channel_progress = dict((sid, dict()) for sid in slides.ids)
        if not self.env.user._is_public() and channel.is_member:
            slide_partners = self.env['slide.slide.partner'].sudo().search([
                ('channel_id', '=', channel.id),
                ('partner_id', '=', self.env.user.partner_id.id),
                ('slide_id', 'in', slides.ids)
            ])
            for slide_partner in slide_partners:
                channel_progress[slide_partner.slide_id.id].update(slide_partner.read()[0])
                if slide_partner.slide_id.question_ids:
                    gains = [slide_partner.slide_id.quiz_first_attempt_reward,
                             slide_partner.slide_id.quiz_second_attempt_reward,
                             slide_partner.slide_id.quiz_third_attempt_reward,
                             slide_partner.slide_id.quiz_fourth_attempt_reward]
                    channel_progress[slide_partner.slide_id.id]['quiz_gain'] = gains[slide_partner.quiz_attempts_count] if slide_partner.quiz_attempts_count < len(gains) else gains[-1]

        if include_quiz:
            quiz_info = slides._compute_quiz_info(self.env.user.partner_id, quiz_done=False)
            for slide_id, slide_info in quiz_info.items():
                channel_progress[slide_id].update(slide_info)

        return channel_progress

    def can_access_with_required(self):
        access = True
        for record in self:
            channel_progress = self.get_channel_progress(record.channel_id)
            all_slides = self.env['slide.slide'].sudo().search([
                ('channel_id', '=', record.channel_id.id)
            ], order=record._order_by_strategy['sequence'])
            _logger.info("============================")
            _logger.info("Channel progress: %r" % channel_progress)
            _logger.info("All slides: %r" % all_slides)
            _logger.info("============================")
            _logger.info("============================")
            for slide in all_slides:
                if slide.id == record.id:
                    break
                completed = channel_progress[slide.id].get('completed')
                _logger.info("slide info: %r" % channel_progress[slide.id])
                _logger.info("slide completed: %r" % completed)
                if slide.slide_required and not completed:
                    access = False

        return access

    def _action_set_completed(self, target_partner):
        access = self.can_access_with_required()
        if not access:
            self_sudo = self.sudo()
            SlidePartnerSudo = self.env['slide.slide.partner'].sudo()
            existing_sudo = SlidePartnerSudo.search([
                ('slide_id', 'in', self.ids),
                ('partner_id', '=', target_partner.id)
            ])
            existing_sudo.write({'completed': False})
            new_slides = self_sudo - existing_sudo.mapped('slide_id')
            SlidePartnerSudo.create([{
                'slide_id': new_slide.id,
                'channel_id': new_slide.channel_id.id,
                'partner_id': target_partner.id,
                'vote': 0,
                'completed': False} for new_slide in new_slides])
        else:
            return super(Slide, self)._action_set_completed(target_partner)
        return True

    def _post_publication(self):
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # for slide in self.filtered(lambda slide: slide.website_published and slide.channel_id.publish_template_id):
        #     publish_template = slide.channel_id.publish_template_id
        #     html_body = publish_template.with_context(base_url=base_url)._render_template(publish_template.body_html, 'slide.slide', slide.id)
        #     subject = publish_template._render_template(publish_template.subject, 'slide.slide', slide.id)
        #     # We want to use the 'reply_to' of the template if set. However, `mail.message` will check
        #     # if the key 'reply_to' is in the kwargs before calling _get_reply_to. If the value is
        #     # falsy, we don't include it in the 'message_post' call.
        #     kwargs = {}
        #     reply_to = publish_template._render_template(publish_template.reply_to, 'slide.slide', slide.id)
        #     if reply_to:
        #         kwargs['reply_to'] = reply_to
        #     slide.channel_id.with_context(mail_create_nosubscribe=True).message_post(
        #         subject=subject,
        #         body=html_body,
        #         subtype='website_slides.mt_channel_slide_published',
        #         email_layout_xmlid='mail.mail_notification_light',
        #         **kwargs,
        #     )
        return True

    def unlink(self):
        if self.question_ids and self.channel_id.channel_partner_ids:
            self.question_ids.unlink()
            self.channel_id.channel_partner_ids.unlink()
        super(Slide, self).unlink()



