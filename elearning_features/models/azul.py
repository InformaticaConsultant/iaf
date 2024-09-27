import base64
import csv
from collections import OrderedDict
from csv import DictWriter
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import ftplib
from io import StringIO, BytesIO
import tempfile
import logging
import pandas as pd
import os


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

_logger = logging.getLogger(__name__)

try:
    import paramiko
except ImportError as err:  # pragma: no cover
    _logger.debug(err)


class AzulReport(models.Model):
    _name = 'azul.payment.report'
    _description = "Azul reports"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_date(self):
        return fields.Date.context_today(self)

    name = fields.Char(string='Nombre')
    state = fields.Selection(
        selection=[
            ('draft', 'Borrado'),
            ('confirm', 'Confirmado'),
            ('cancel', 'Cancelado')
        ],
        string='Estado',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )
    report_date = fields.Date(
        string='Fecha',
        index=True,
        copy=False,
        default=_get_default_date)
    payment_ids = fields.Many2many(
        comodel_name='account.payment',
        string='Pagos',
        states={'draft': [('readonly', False)]},
    )
    report_type = fields.Selection(
        selection=[
            ('access', 'Accesos'),
            ('ncf', 'Generar NCF'),
            ('payment', 'Pagos'),
            ('payment_without_access', 'Pagos sin acceso'),
        ],
        string='Tipo de reporte',
        states={'draft': [('readonly', False)]},
    )
    ncf_file = fields.Binary(string='Archivo para NCF')
    ncf_filename = fields.Char(string='Nombre del archivo')
    payment_file = fields.Binary(string='Archivo para Pagos')
    payment_filename = fields.Char(string='Nombre del archivo')
    payment_without_access_file = fields.Binary(
        string='Archivo para Pagos sin acceso')
    payment_without_access_filename = fields.Char(string='Nombre del archivo')
    access_file = fields.Binary(string='Archivo acceso')
    access_filename = fields.Char(string='Nombre del archivo')

    def process_report_queue(self):
        self.info_for_invoice()
        self.payment_details()
        self.payment_without_access()
        self.slide_access()

    def create_record(self, report_type, date):
        if report_type == 'ncf':
            name = "Generar NCF - %s" % date
        elif report_type == 'access':
            name = "Reporte accesos - %s" % date
        elif report_type == 'payment_without_access':
            name = "Reporte pagos sin accesos - %s" % date
        else:
            name = "Contable pagos - %s" % date
        self.create({
            'name': name,
            'date': date,
            'report_type': report_type,
        })

        return True

    def action_report(self):
        if self.report_type == 'ncf':
            self.info_for_invoice()
        elif self.report_type == 'payment':
            self.payment_details()
        elif self.report_type == 'payment_without_access':
            self.payment_without_access()
        elif self.report_type == 'access':
            self.slide_access()

    def info_for_invoice(self):
        """
        Create CSV file with payment info to allow BPD create customer invoices
        """
        # self.date = date.today() + relativedelta(days=-1)
        payment_ids = []
        # self = self.create_record('ncf', self.date)
        buffer = StringIO()
        buffer.seek(0)

        payments = self.env['account.payment'].search([
            ('state', 'not in', ['draft', 'cancel']),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('partner_id', '!=', False),
            ('was_send', '=', False),
            ('payment_date', '=', self.report_date),
            ('payment_transaction_id', '!=', False),
        ])

        columns = ['ID', 'Nombre', 'Cedula', 'Monto', 'Descripcion',
                   'TipoCobro', 'Fecha']
        file_path = '/tmp/Gen_NCF.csv'
        csvwriter = DictWriter(buffer, columns, delimiter=',', dialect='excel')
        csvwriter.writeheader()
        # encoding="utf-8-sig"
        with open(file_path, 'w+', encoding="utf-8-sig", newline='') as f:

            for payment in payments:
                txt = payment.payment_transaction_id
                if txt.azul_response_message not in ['VALIDADA', 'APROBADA']:
                    continue

                description = "Pago a través del portal Academia Digital: "
                for order in txt.sale_order_ids:
                    if order.channel_id:
                        description += order.channel_id.name
                    else:
                        for line in order.order_line:
                            if line.event_id:
                                description += line.event_id.name

                amount = str(payment.amount).replace(',', '')
                data = {
                    'ID': txt.azul_txn_id,
                    'Nombre': payment.partner_id.name,
                    'Cedula': payment.partner_id.vat,
                    'Monto': amount,
                    'Descripcion': description,
                    'TipoCobro': "D",
                    'Fecha': payment.payment_date.strftime("%Y%m%d"),
                }
                csvwriter.writerow(data)
                payment_ids.append(payment.id)

        pathname = file_path
        filename = file_path.replace('/tmp/', '')
        self.ftp_send_file(pathname, filename)
        datas = base64.encodebytes(buffer.getvalue().encode('utf-8-sig'))
        # self.ftp_send_file(file_path, filename)
        self.env['ir.attachment'].create({
            'name': filename,
            'datas': datas,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        self.write({
            'payment_ids': [(6, 0, payment_ids)],
            'ncf_filename': filename,
            'ncf_file': datas,
        })

    def payment_details(self):
        """
        This function search payments and create a csv file with it.
        """
        buffer = StringIO()
        buffer.seek(0)
        # self.date = date.today() + relativedelta(days=-1)
        payment_ids = []
        # self = self.
        # ('payment', self.date)

        payments = self.env['account.payment'].search([
            ('state', 'not in', ['draft', 'cancel']),
            ('partner_type', '=', 'customer'),
            ('was_send', '=', False),
            ('payment_date', '=', self.report_date),
            ('payment_transaction_id', '!=', False),
        ])
        columns = [
            'ID', 'nombre', 'tipo_doc', 'documento', 'monto',
            'descripcion_capacitacion', 'cod_aut', 'num_ref', 'marca',
            'descripcion_trans', 'fecha_capacitacion', 'estatus_transaccion',
            'usuario',
        ]
        _logger.info("Pagos: %r " % payments)
        file_path = '/tmp/contable_pagos.csv'
        csvwriter = DictWriter(buffer, columns, delimiter=',', dialect='excel')
        csvwriter.writeheader()

        with open(file_path, 'w+', encoding="utf-8-sig", newline='') as f:
            for payment in payments:
                _logger.info("Ref pago: %s " % payment.name)
                payment_ids.append(payment.id)
                vat = payment.partner_id.vat
                txt = payment.payment_transaction_id
                if txt.azul_response_message not in ['VALIDADA', 'APROBADA']:
                    continue
                description = "Pago a través del portal Academia Digital: "
                fecha_cap = False
                course_or_event = False
                for order in txt.sale_order_ids:
                    if order.channel_id:
                        course_or_event = order.channel_id.name
                        description += order.channel_id.name
                        fecha_cap = order.channel_id.start_date.strftime(
                            '%Y%m%d')
                    else:
                        for line in order.order_line:
                            if line.event_id:
                                course_or_event = line.event_id.name
                                fecha_cap = line.event_id.date_begin.strftime(
                                    "%Y%m%d")
                                description += line.event_id.name
                if not vat or not description:
                    continue

                if len(vat) == 11:
                    tipo_doc = "cedula"
                elif len(vat) == 9 and isdigit(vat):
                    tipo_doc = "rnc"
                else:
                    tipo_doc = "pasaporte"

                data = {
                    'ID': txt.azul_txn_id,
                    'nombre': payment.partner_id.name,
                    'tipo_doc': str(tipo_doc),
                    'documento': vat,
                    'monto': payment.amount,
                    'descripcion_capacitacion': description,
                    'cod_aut': txt.azul_auth_code,
                    'num_ref': str(txt.azul_rrn),
                    'marca': txt.azul_card_number_type,
                    'descripcion_trans': course_or_event,
                    'fecha_capacitacion': fecha_cap,
                    'estatus_transaccion': txt.azul_response_message,
                    'usuario': txt.azul_user_id.login,
                }
                payment_ids.append(payment.id)
                csvwriter.writerow(data)

        pathname = file_path
        filename = file_path.replace('/tmp/', '')
        self.ftp_send_file(pathname, filename)
        datas = base64.encodebytes(buffer.getvalue().encode('utf-8-sig'))
        # self.ftp_send_file(file_path, filename)
        self.env['ir.attachment'].create({
            'name': filename,
            'datas': datas,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        self.write({
            'payment_ids': [(6, 0, payment_ids)] if payment_ids else False,
            'payment_filename': filename,
            'payment_file': datas,
        })

    def payment_without_access(self):
        """
        This function search slide access and create a csv file with it.
        """
        buffer = StringIO()
        buffer.seek(0)
        channel_partner_obj = self.env['slide.channel.partner']
        payment_transactions = False
        payment_ids = []
        # self.report_date = date.today() + relativedelta(days=-1)
        # self = self.create_record('payment_without_access', self.date)

        # self.date = date.today() + relativedelta(days=-1)
        slides = self.env['slide.channel'].search([
            # ('start_date', '<=', self.report_date),
            ('website_published', '=', True),
            ('enroll', '=', 'payment'),
            ('product_id', '!=', False),
        ])

        yesterday_dt_date = datetime.now() + relativedelta(days=-1)
        events = self.env['event.event'].search([
            # ('date_begin', '<=', yesterday_dt_date),
            ('is_published', '=', True),
        ]).filtered(lambda e: e.event_ticket_ids.filtered(
            lambda t: t.price > 0))

        produc_ids = self.env['product.product']
        for slide in slides:
            for scp in slide.channel_partner_ids.filtered(
                    lambda p: p.completion == 0):
                produc_ids |= slide.product_id

        for event in events:
            for ticket in event.event_ticket_ids:
                produc_ids |= ticket.product_id

        sales = self.env['sale.order.line'].search([
            ('product_id', 'in', produc_ids.ids),
        ]).mapped('order_id')

        if not sales:
            raise ValidationError(
                "No hay ventas registrada para esa fecha.")

        transactions = self.env['payment.transaction']
        payment_transactions = self.env['payment.transaction'].search([
            ('sale_order_ids', 'in', sales.ids),
            ('state', 'in', ['authorized', 'done']),
            ('azul_response_message', 'in', ['VALIDADA', 'APROBADA']),
        ])
        transactions |= payment_transactions

        columns = [
            'fecha_pago', 'tipo_id', 'ID', 'monto', 'descripcion_transaccion',
            'estatus_transaccion', 'descripcion_capacitacion',
            'fecha_capacitacion', 'cod_aut', 'num_ref',
        ]

        _logger.info("pagos sin acceso")
        _logger.info("Ventas %r " % sales)
        _logger.info("Pagos %r | %r " % (payment_transactions, transactions))

        file_path = '/tmp/reporte_sin_acceso_clientes.csv'
        csvwriter = DictWriter(buffer, columns, delimiter=',', dialect='excel')
        csvwriter.writeheader()
        with open(file_path, 'w+', encoding="utf-8-sig", newline='') as f:
            for tx in transactions:
                _logger.info("Ref: %s " % tx.reference)
                course_started = False
                payment_date = False
                if tx.payment_id:
                    payment_ids.append(tx.payment_id.id)
                    payment_date = tx.payment_id.payment_date.strftime(
                        "%Y-%m-%d")
                else:
                    payment_date = tx.date.strftime("%Y-%m-%d")

                vat = tx.partner_id.vat
                course_or_event = ""
                description = "Pago a través del portal Academia Digital:  "
                fecha_cap = False

                for order in tx.sale_order_ids:
                    if order.channel_id:
                        channel_partner = channel_partner_obj.search([
                            ('channel_id', '=', order.channel_id.id),
                            ('partner_id', '=', order.partner_id.id),
                        ])
                        if channel_partner.completion > 0:
                            course_started = True
                        course_or_event = order.channel_id.name
                        fecha_cap = order.channel_id.start_date.strftime(
                            '%Y-%m-%d')
                        description += order.channel_id.name
                    else:
                        for line in order.order_line:
                            if line.event_id:
                                course_or_event = line.event_id.name
                                fecha_cap = line.event_id.date_begin.strftime(
                                    "%Y-%m-%d")
                                description += line.name

                if course_started:
                    continue

                if len(vat) == 11:
                    tipo_doc = "cedula"
                elif len(vat) == 9 and isdigit(vat):
                    tipo_doc = "rnc"
                else:
                    tipo_doc = "pasaporte"

                data = {
                    'fecha_pago': payment_date,
                    'tipo_id': str(tipo_doc),
                    'ID': vat,
                    'monto': str(tx.amount).replace(',', ''),
                    'descripcion_transaccion': description[:50],
                    'estatus_transaccion': tx.azul_response_message,
                    'descripcion_capacitacion': course_or_event,
                    'fecha_capacitacion': fecha_cap,
                    'cod_aut': tx.azul_auth_code,
                    'num_ref': str(tx.azul_rrn),
                }
                csvwriter.writerow(data)

        pathname = file_path
        filename = file_path.replace('/tmp/', '')
        self.ftp_send_file(pathname, filename)
        datas = base64.encodebytes(buffer.getvalue().encode('utf-8-sig'))
        # self.ftp_send_file(file_path, filename)
        self.env['ir.attachment'].create({
            'name': filename,
            'datas': datas,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        self.write({
            'payment_ids': [(6, 0, payment_ids)] if payment_ids else False,
            'payment_without_access_filename': filename,
            'payment_without_access_file': datas,
        })

    def slide_access(self):
        """
        This function search slide access and create a csv file with it.
        """
        buffer = StringIO()
        buffer.seek(0)
        payment_transactions = False
        payment_ids = []
        # self.date = date.today() + relativedelta(days=-1)
        # self = self.create_record('access', self.date)

        slides = self.env['slide.channel'].search([
            # ('start_date', '<=', self.date),
            ('website_published', '=', True),
            ('enroll', '=', 'payment'),
            ('product_id', '!=', False),
        ])

        yesterday_dt_date = datetime.now() + relativedelta(days=-1)
        events = self.env['event.event'].search([
            ('date_begin', '<', yesterday_dt_date),
            ('is_published', '=', True),
        ]).filtered(lambda e: e.event_ticket_ids.filtered(
            lambda t: t.price > 0))

        produc_ids = slides.mapped('product_id')
        for event in events:
            for ticket in event.event_ticket_ids:
                produc_ids |= ticket.product_id

        sales = self.env['sale.order.line'].search([
            ('product_id', 'in', produc_ids.ids),
        ]).mapped('order_id')

        if not sales:
            raise ValidationError("No hay ventas registrada para esa fecha.")

        transactions = self.env['payment.transaction']
        payment_transactions = self.env['payment.transaction'].search([
            ('sale_order_ids', 'in', sales.ids),
            ('state', 'in', ['authorized', 'done']),
            ('azul_response_message', 'in', ['VALIDADA', 'APROBADA']),
        ])
        transactions |= payment_transactions

        _logger.info("pagos con acceso")
        _logger.info("Ventas %r " % sales)
        _logger.info("Pagos %r | %r " % (payment_transactions, transactions))
        columns = [
            'fecha_capacitacion', 'descripcion_capacitacion', 'tipo_id', 'ID',
            'pagada', 'usuario'
        ]

        file_path = '/tmp/reporte_accesos.csv'
        csvwriter = DictWriter(buffer, columns, delimiter=',', dialect='excel')
        csvwriter.writeheader()

        with open(file_path, 'w+', encoding="utf-8-sig", newline='') as f:
            for tx in transactions:
                _logger.info("Ref: %s " % tx.reference)
                course_not_started = False
                if tx.payment_id:
                    payment_ids.append(tx.payment_id.id)

                vat = tx.partner_id.vat
                description = "Pago a través del portal Academia Digital: "
                start_date = False
                event_date = False
                for order in tx.sale_order_ids:
                    if order.channel_id:
                        channel_partner = self.env[
                            'slide.channel.partner'].search([
                                ('channel_id', '=', order.channel_id.id),
                                ('partner_id', '=', order.partner_id.id),
                            ])
                        if channel_partner.completion == 0:
                            course_not_started = True

                        start_date = order.channel_id.start_date.strftime(
                            '%Y-%m-%d')
                        description += order.channel_id.name
                    else:
                        for line in order.order_line:
                            if line.event_id:
                                event_date = line.event_id.date_begin.strftime(
                                    "%Y-%m-%d")
                                description += line.event_id

                if course_not_started:
                    continue

                if len(vat) == 11:
                    tipo_doc = "cedula"
                elif len(vat) == 9 and isdigit(vat):
                    tipo_doc = "rnc"
                else:
                    tipo_doc = "pasaporte"

                data = {
                    'fecha_capacitacion': start_date or event_date,
                    'descripcion_capacitacion': description,
                    'tipo_id': str(tipo_doc),
                    'ID': vat,
                    'pagada': "Si",
                    'usuario': tx.partner_id.email,
                }
                csvwriter.writerow(data)
        csvwriter.close()
        pathname = file_path.replace('/tmp/', '')
        filename = file_path.replace('/tmp/', '')
        self.ftp_send_file(pathname, filename)
        datas = base64.encodebytes(buffer.getvalue().encode('utf-8-sig'))
        # self.ftp_send_file(file_path, filename)
        self.env['ir.attachment'].create({
            'name': filename,
            'datas': datas,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        self.write({
            'payment_ids': [(6, 0, payment_ids)] if payment_ids else False,
            'access_filename': filename,
            'access_file': datas,
        })

    def ftp_send_file(self, path, filename):
        ICP = self.env['ir.config_parameter'].sudo()
        ftp_url = ICP.get_param('elearning_features.ftp_url')
        ftp_username = ICP.get_param('elearning_features.ftp_login')
        ftp_password = ICP.get_param('elearning_features.ftp_password')
        client = False

        try:
            transport = paramiko.Transport(ftp_url)
            transport.connect(username=ftp_username, password=ftp_password)
            client = paramiko.SFTPClient.from_transport(transport)
            client.put(path, 'Reportes/' + filename)
        except Exception as e:
            pass

        if client:
            client.close()  # close file and FTP


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    was_send = fields.Boolean()
