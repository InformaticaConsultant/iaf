# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import hashlib
import logging
import mimetypes
import os
import re
import sys
import traceback

import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls
import werkzeug.utils

import odoo
from odoo import api, http, models, tools, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request, content_disposition
from odoo.tools import consteq, pycompat
from odoo.tools.mimetypes import guess_mimetype
from odoo.modules.module import get_resource_path, get_module_path

from odoo.tools.misc import str2bool


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None, special_access=False):
        record, status = self._get_record_and_check(xmlid=xmlid, model=model, id=id, field=field, access_token=access_token,special_access=special_access)

        if not record:
            return (status or 404, [], None)

        content, headers, status = None, [], None

        if record._name == 'ir.attachment':
            status, content, filename, mimetype, filehash = self._binary_ir_attachment_redirect_content(record, default_mimetype=default_mimetype)
        if not content:
            status, content, filename, mimetype, filehash = self._binary_record_content(
                record, field=field, filename=filename, filename_field=filename_field,
                default_mimetype='application/octet-stream')

        status, headers, content = self._binary_set_headers(
            status, content, filename, mimetype, unique, filehash=filehash, download=download)

        return status, headers, content

    def _get_record_and_check(self, xmlid=None, model=None, id=None, field='datas', access_token=None, special_access=False):
            # get object and content
        record = None
        if xmlid:
            record = self._xmlid_to_obj(self.env, xmlid)
        elif id and model in self.env:
            record = self.env[model].browse(int(id))

        # obj exists
        if not record or not record.exists() or field not in record:
            return None, 404


        if model=="slide.slide" and special_access != "" and bool(special_access):
            record_sudo = record.sudo()
            record = record_sudo
            return record, 200

        if model == 'ir.attachment':
            record_sudo = record.sudo()
            if access_token and not consteq(record_sudo.access_token or '', access_token):
                return None, 403
            elif (access_token and consteq(record_sudo.access_token or '', access_token)):
                record = record_sudo
            elif record_sudo.public:
                record = record_sudo
            elif self.env.user.has_group('base.group_portal'):
                # Check the read access on the record linked to the attachment
                # eg: Allow to download an attachment on a task from /my/task/task_id
                record.check('read')
                record = record_sudo

        # check read access
        try:
            # We have prefetched some fields of record, among which the field
            # 'write_date' used by '__last_update' below. In order to check
            # access on record, we have to invalidate its cache first.
            record._cache.clear()
            record['__last_update']
        except AccessError:
            return None, 403

        return record, 200
