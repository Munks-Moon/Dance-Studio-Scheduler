from calendar import HTMLCalendar
from calendar import HTMLCalendar
from itertools import groupby
from django.utils.html import conditional_escape as esc
from django.urls import reverse

# Custom HTMLCalendar
class TimeSlotCalendar(HTMLCalendar):
    def __init__(self, time_slots, user):
        super(TimeSlotCalendar, self).__init__()
        self.time_slots = self.group_by_day(time_slots)
        self.user = user
        self.year = None
        self.month = None

    def group_by_day(self, time_slots):
        field = lambda time_slot: time_slot.date.day
        return dict(
            [(day, list(items)) for day, items in groupby(time_slots, field)]
        )
    
    def formatweekheader(self):
        headers = [self.formatweekday(i) for i in self.iterweekdays()]
        return '<tr class="calendar-header">' + ''.join(headers) + '</tr>'
    
    def formatmonth(self, theyear, themonth, withyear=True):
        self.year = theyear
        self.month = themonth 
        return super(TimeSlotCalendar, self).formatmonth(theyear, themonth, withyear=withyear)

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>' 
        else:
            time_slots = self.time_slots.get(day, [])
            time_slots_html = []
            for time_slot in time_slots:
                client = time_slot.client
                if self.user.is_superuser and client:
                    client_url = reverse('user-profile', args=[client.id])
                    client_link = f'<a href="{client_url}">{client}</a>'
                else:
                    client_link = ''
                end_time_str = time_slot.end_time() if callable(time_slot.end_time) else time_slot.end_time
                
                start_time_12hr = time_slot.start_time.strftime("%I:%M %p")
                end_time_str_12hr = end_time_str.strftime("%I:%M %p")

                time_slots_html.append(f'<li class="time-slot"> {esc(start_time_12hr[:5])} - {esc(end_time_str_12hr)} {client_link} </li>')

            day_url = reverse('timeslot-calendar-link', args=[f"{self.year}-{self.month:02}-{day:02}"])
            clickable_day = f'<a href="{day_url}">{day}</a>'

            return f'<td class="{self.cssclasses[weekday]} calendar-cell"><span class="date">{clickable_day}</span><ul class="time-slot-list">{"".join(time_slots_html)}</ul></td>'
            

	