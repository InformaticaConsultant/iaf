# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date

from odoo import api, fields, models, _, exceptions

_logger = logging.getLogger(__name__)


class BadgeUser(models.Model):
    _inherit = 'gamification.badge.user'

    def _send_badge(self):
        # template = self.env.ref(
        #     'elearning_features.email_template_badge_received')
        #
        # for badge_user in self:
        #     self.env['mail.thread'].message_post_with_template(
        #         template.id,
        #         model=badge_user._name,
        #         res_id=badge_user.id,
        #         composition_mode='mass_mail',
        #     )
        return True
