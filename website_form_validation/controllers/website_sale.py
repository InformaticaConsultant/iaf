# ©  2015-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo.http import request

from odoo import tools
from odoo.addons.phone_validation.tools import phone_validation
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import content_disposition, Controller, request, route


class WebsiteFormValidation(WebsiteSale):
    def checkout_form_validate(self, mode, all_form_values, data):
        error = dict()
        error_message = []

        if data.get("phone"):
            data["phone"] = data.get("phone").strip()

        if data.get("zip"):
            data["zip"] = data.get("zip").strip()

        standard_error, standard_error_message = super(WebsiteFormValidation, self).checkout_form_validate(
            mode, all_form_values, data
        )
        error.update(standard_error)
        error_message += standard_error_message

        if data.get("phone"):
            try:
                phone = data.get("phone")
                country = request.env["res.country"].sudo().browse(data.get("country_id"))
                data["phone"] = phone_validation.phone_format(
                    phone,
                    country.code if country else None,
                    country.phone_code if country else None,
                    force_format="INTERNATIONAL",
                    raise_exception=True,
                )
            except Exception as e:
                error["phone"] = "error"
                error_message.append("Teléfono inválido. Solo dígitos, sin () "
                                     "o -")
        if not data.get("zip").isdigit():
            error["zip"] = "error"
            error_message.append("Código postal no válido. Solo se aceptan "
                                 "dígitos.")

        return error, error_message


class PortalAccount(CustomerPortal):

    def details_form_validate(self, data):
        error, error_message = super(PortalAccount, self).details_form_validate(data)
        # prevent VAT/name change if invoices exist
        partner = request.env['res.users'].browse(request.uid).partner_id

        if data.get("vat"):
            data["vat"] = data.get("vat").strip()

        if data.get("vat"):
            data["vat"] = data.get("vat").strip()

        if data.get("zipcode"):
            data["zipcode"] = data.get("zipcode").strip()

        if data.get("phone"):
            data["phone"] = data.get("phone").strip()

        if data.get("name"):
            data["name"] = data.get("name").strip()

        if not data['name'].replace(" ", "").isalpha():
            error["name"] = "error"
            error_message.append("Nombre inválido. Solo se aceptan caracteres alfabéticos.")

        if not data['vat'].isdigit():
            error["vat"] = "error"
            error_message.append("NIF inválido. Solo se aceptan dígitos.")
            # Cédula invalida
            # NIF inválido

        if data['zipcode'] and not data['zipcode'].isdigit():
            error["zipcode"] = "error"
            error_message.append("Código postal inválido. Solo "
                                 "se aceptan dígitos.")

        if data.get('email') and not tools.single_email_re.match(data.get(
                'email')):
            error["email"] = 'error'
            error_message.append('Correo inválido. Introduza un correo válido.')

        return error, error_message


