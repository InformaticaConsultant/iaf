import json
import logging
import pytz
import werkzeug
from werkzeug.urls import url_encode


from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
GOOGLE_CALENDAR_URL = 'https://www.google.com/calendar/render?'


class EventType(models.Model):
    _inherit = 'event.type'

    @api.model
    def _get_default_event_type_mail_ids(self):
        super(EventType, self)._get_default_event_type_mail_ids()
        return [(0, 0, {
            'notification_type': 'mail',
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref(
                'elearning_features.event_subscription').id,
        }), (0, 0, {
            'notification_type': 'mail',
            'interval_nbr': 1,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref(
                'elearning_features.event_reminder').id,
        }), (0, 0, {
            'notification_type': 'mail',
            'interval_nbr': 10,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref(
                'elearning_features.event_reminder').id,
        })]


class Event(models.Model):
    _inherit = "event.event"

    def _is_event_registrable(self):
        return self.date_end > fields.Datetime.now()

    @api.depends('name')
    def _compute_website_url(self):
        super(Event, self)._compute_website_url()
        for event in self:
            # avoid to perform a slug on a not yet saved record in case of
            # an onchange.
            if event.id:
                event.website_url = '/eventos/%s' % slug(event)

    def _create_menu(self, sequence, name, url, xml_id):
        if not url:
            self.env['ir.ui.view'].with_context(_force_unlink=True).search([
                ('name', '=', name + ' ' + self.name)]).unlink()
            newpath = self.env['website'].new_page(
                name + ' ' + self.name, template=xml_id, ispage=False)['url']
            url = "/eventos/" + slug(self) + "/page/" + newpath[1:]
        menu = self.env['website.menu'].create({
            'name': name,
            'url': url,
            'parent_id': self.menu_id.id,
            'sequence': sequence,
            'website_id': self.website_id.id,
        })
        return menu

    def _get_event_resource_urls(self):
        url_date_start = self.date_begin.strftime('%Y%m%dT%H%M%SZ')
        url_date_stop = self.date_end.strftime('%Y%m%dT%H%M%SZ')
        params = {
            'action': 'TEMPLATE',
            'text': self.name,
            'dates': url_date_start + '/' + url_date_stop,
            'details': self.name,
        }
        if self.address_id:
            params.update(
                location=self.sudo().address_id.contact_address.replace(
                    '\n', ' '))
        encoded_params = url_encode(params)
        google_url = GOOGLE_CALENDAR_URL + encoded_params
        iCal_url = '/event/%d/ics?%s' % (self.id, encoded_params)
        return {'google_url': google_url, 'iCal_url': iCal_url}

    def get_image_path(self):

        path_img = ""

        for record in self:
            data = json.loads(record.cover_properties)
            path_img = data.get('background-image')
            path_img = path_img.replace('(', '').replace(')', '').replace(
                '\'', '').replace('url', '')

        if not path_img or path_img == 'none':
            path_img = "/elearning_features/static/src/img/eventos/portada3.jpg"
    
        return path_img


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'event_badge'
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref(
            'elearning_features.event_registration_mail_template_badge')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='event.registration',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

