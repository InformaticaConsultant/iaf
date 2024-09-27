import logging

from odoo.tools.translate import _
from odoo.exceptions import UserError

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    def _send_email(self):
        """ send notification email to a new portal user """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User '
                              'Preferences to send emails.'))

        # determine subject and body in the portal user's language
        template = self.env.ref(
            'elearning_features.mail_template_data_portal_welcome')
        for wizard_line in self:
            lang = wizard_line.user_id.lang
            partner = wizard_line.user_id.partner_id

            portal_url = partner.with_context(
                signup_force_type_in_url='',
                lang=lang)._get_signup_url_for_action()[partner.id]
            partner.signup_prepare()

            if template:
                template.with_context(
                    dbname=self._cr.dbname, portal_url=portal_url,
                    lang=lang).send_mail(wizard_line.id, force_send=True)
            else:
                _logger.warning("No email template found for sending email "
                                "to the portal user")
        return True
