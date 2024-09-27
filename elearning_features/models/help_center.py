import logging
import re

from odoo import fields, models, api, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import misc
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)


class HelpCenter(models.Model):
    _name = 'website.help.center'
    _description = 'Help Center page'
    _inherit = ['mail.thread', 'image.mixin', 'website.seo.metadata',
                'website.multi.mixin']
    _order = "sequence"

    @api.model
    def _get_default_faq(self):
        with misc.file_open('elearning_features/data/default_faq.html',
                'r') as f:
            return f.read()

    name = fields.Char('Topic', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1)
    faq = fields.Html(
        string='Guidelines',
        default=_get_default_faq,
        translate=html_translate,
        sanitize=False,
    )
    active = fields.Boolean(string="Activo", default=True, )

    @api.model
    def create(self, values):
        return super(HelpCenter, self.with_context(mail_create_nolog=True,
            mail_create_nosubscribe=True)).create(values)

