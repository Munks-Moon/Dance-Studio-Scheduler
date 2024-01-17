from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import TimeSlot
from datetime import timedelta

class Command(BaseCommand):
    help = 'Updates the  status of timeslots to completed if their date has passed'

    def handle(self, *args, **kwargs):
        yesterday = timezone.now().date() - timedelta(days=1)
        expired_timeslots = TimeSlot.objects.filter(date__lt=yesterday, status='confirmed')
        
        for timeslot in expired_timeslots:
            timeslot.status = 'completed'
            timeslot.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {expired_timeslots.count()} timeslots.'))