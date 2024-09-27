# -*- coding: utf-8 -*-

import logging
import werkzeug
from werkzeug.exceptions import NotFound, Forbidden
from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.mail import _check_special_access, \
    SlidesPortalChatter
from odoo.tools import plaintext2html, html2plaintext

_logger = logging.getLogger(__name__)


class SlidesChatter(SlidesPortalChatter):

    @http.route([
        '/cursos/mail/update_comment',
        '/slides/mail/update_comment',
        '/mail/chatter_update',
        ], type='http', auth="user", methods=['POST'])
    def mail_update_message(self, res_model, res_id, message, message_id, redirect=None, attachment_ids='', attachment_tokens='', **post):
        # keep this mecanism intern to slide currently (saas 12.5) as it is
        # considered experimental
        if res_model != 'slide.channel':
            raise Forbidden()
        res_id = int(res_id)

        attachment_ids = [int(attachment_id) for attachment_id in attachment_ids.split(',') if attachment_id]
        attachment_tokens = [attachment_token for attachment_token in attachment_tokens.split(',') if attachment_token]
        self._portal_post_check_attachments(attachment_ids, attachment_tokens)

        pid = int(post['pid']) if post.get('pid') else False
        if not _check_special_access(res_model, res_id, token=post.get('token'), _hash=post.get('hash'), pid=pid):
            raise Forbidden()

        # fetch and update mail.message
        message_id = int(message_id)
        message_body = plaintext2html(message)
        domain = [
            ('model', '=', res_model),
            ('res_id', '=', res_id),
            ('website_published', '=', True),
            ('author_id', '=', request.env.user.partner_id.id),
            ('message_type', '=', 'comment'),
            ('id', '=', message_id)
        ]  # restrict to the given message_id
        message = request.env['mail.message'].search(domain, limit=1)
        if not message:
            raise NotFound()
        message.write({
            'body': message_body,
            'attachment_ids': [(4, aid) for aid in attachment_ids],
        })

        # update rating
        if post.get('rating_value'):
            domain = [
                ('res_model', '=', res_model),
                ('res_id', '=', res_id),
                ('website_published', '=', True),
                ('message_id', '=', message.id),
            ]
            rating = request.env['rating.rating'].search(
                domain, order='write_date DESC', limit=1)
            rating.write({
                'rating': float(post['rating_value']),
                'feedback': html2plaintext(message.body),
            })

        # redirect to specified or referrer or simply channel page as fallback
        redirect_url = redirect or (
                request.httprequest.referrer and request.httprequest.referrer +
                '#review') or '/slides/%s' or '/cursos/%s' % res_id
        _logger.info("Redirect commentp post #1: %r" % post)
        _logger.info("Redirect commentp post #2: %r" % redirect)
        _logger.info("Redirect comment #3: %r" % request.httprequest.referrer)
        _logger.info("Redirect comment #4: %r" % (
                request.httprequest.referrer and request.httprequest.referrer +
                '#review') or '/slides/%s' or '/cursos/%s' % res_id)
        _logger.info("Redirect commentp post #5 %r" % redirect_url)
        return werkzeug.utils.redirect(redirect_url, 302)
