import calendar

from odoo import api, fields, models, SUPERUSER_ID, _
import datetime

class Website(models.Model):
    _inherit = 'website'

    def get_last_slide(self, limit=3):
        SlideSlide = self.env['slide.channel']
        slides = SlideSlide.search([
            ('active', '=', True)
        ], order="create_date, id desc", limit=limit)
        return slides

    def get_last_blogs(self, limit=10):
        BlogPost = self.env['blog.post']
        slides = BlogPost.search([
            ('active', '=', True)
        ], order="create_date, id desc", limit=limit)
        return slides

    def get_last_events(self, limit=4):
        Events = self.env['event.event']

        domain = [
            ('state', '!=', 'cancel'),
            ('date_end', '>=', datetime.datetime.combine(
                fields.Date.context_today(self), datetime.time(0, 0, 0)))]
        slides = Events.search(
            domain, order="create_date, id desc", limit=limit)
        return slides

    def get_slide_date_format(self, slide):
        week_day_dict = {
            1: 'Lunes',
            2: 'Martes',
            3: 'Miércoles',
            4: 'Jueves',
            5: 'Viernes',
            6: 'Sábado',
            7: 'Domingo',
        }
        month_name_dict = {
            'January': 'Enero',
            'February': 'Febrero',
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'October': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre',
        }
        if slide.start_date:
            day_name = week_day_dict[slide.start_date.isoweekday()]
            month = calendar.month_name[slide.start_date.month]
            month_name = month_name_dict[month]
            dt_formatted = "%s %d de %s" % (day_name, slide.start_date.day,
                                            month_name)
            return dt_formatted
        return "Curso no tiene fecha"

    def get_event_date_format(self, event):
        week_day_dict = {
            1: 'Lunes',
            2: 'Martes',
            3: 'Miércoles',
            4: 'Jueves',
            5: 'Viernes',
            6: 'Sábado',
            7: 'Domingo',
        }
        month_name_dict = {
            'January': 'Enero',
            'February': 'Febrero',
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'Octuber': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre',
        }
        if event.date_begin:
            day_name = week_day_dict[event.date_begin.isoweekday()]
            month = calendar.month_name[event.date_begin.month]
            month_name = month_name_dict[month]
            dt_formatted = "%s %d de %s" % (day_name, event.date_begin.day,
                                            month_name)
            return dt_formatted
        return "Evento no tiene fecha"

