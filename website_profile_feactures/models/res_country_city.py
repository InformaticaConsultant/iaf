from odoo import models, fields, api, _


class ResCountryCity(models.Model):
    _name = 'res.country.city'
    _description = "Country province"
    _order = 'name'

    name = fields.Char(string="Nombre", required=True)
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Provincia",
        required=True,
    )

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result