from odoo import models, fields, api, _


class ResCountryTown(models.Model):
    _name = 'res.country.town'
    _description = "Country town"
    _order = 'code, state_id'

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string='Código', required=True)
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Provincia",
        required=True,
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="País",
    )

    _sql_constraints = [
        ('name_code_uniq', 'unique(country_id, code)',
         'El código del Municipio debe ser único por país!')
    ]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        args = args or []
        if self.env.context.get('country_id'):
            args = expression.AND([args, [
                ('country_id', '=', self.env.context.get('country_id'))]])

        if operator == 'ilike' and not (name or '').strip():
            first_domain = []
            domain = []
        else:
            first_domain = [('code', '=ilike', name)]
            domain = [('name', operator, name)]

        first_town_ids = self._search(expression.AND(
            [first_domain, args]), limit=limit,
            access_rights_uid=name_get_uid) if first_domain else []
        town_ids = first_town_ids + [town_id for town_id in self._search(
            expression.AND([domain, args]), limit=limit,
            access_rights_uid=name_get_uid) if not town_id in first_town_ids]
        return models.lazy_name_get(
            self.browse(town_ids).with_user(name_get_uid))

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} ({})".format(record.name,
                                                       record.country_id.code)))
        return result