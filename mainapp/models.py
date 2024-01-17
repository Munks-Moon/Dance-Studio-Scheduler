from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta, date

class CustomUser(AbstractUser):

    PROVINCE_CHOICES = (
    ('AB', 'Alberta'),
    ('BC', 'British Columbia'),
    ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'),
    ('NL', 'Newfoundland and Labrador'),
    ('NS', 'Nova Scotia'),
    ('ON', 'Ontario'),
    ('PE', 'Prince Edward Island'),
    ('QC', 'Quebec'),
    ('SK', 'Saskatchewan'),
    ('NT', 'Northwest Territories'),
    ('NU', 'Nunavut'),
    ('YT', 'Yukon'),
    )

    # Dancer Information
    dancer_full_name = models.CharField(max_length=50)
    dancer_date_of_birth = models.DateField(blank=True, null=True)

    # Parent Information
    parent_full_name = models.CharField(max_length=100)
    parent_email = models.EmailField(unique=True)
    parent_phone = models.CharField(max_length=10, blank=True)

    # Address Information
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICES, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Additional Client Information
    emergency_contact_full_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models. CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class TimeSlot(models.Model):

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]

    date = models.DateField(default=date.today)
    start_time = models.TimeField()
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    is_new = models.BooleanField(default=True)

    class Meta:
        unique_together = [['start_time', 'date']]
        ordering = ["date", "start_time"]

    def end_time(self):
        dt = datetime.combine(datetime.min.date(), self.start_time)
        dt += timedelta(hours=1)
        return dt.time()

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} {self.start_time.strftime('%I:%M %p')} - {self.end_time().strftime('%I:%M %p')}"

class CanceledTimeSlot(models.Model):

    date = models.DateField(default=date.today)
    start_time = models.TimeField()
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def end_time(self):
        dt = datetime.combine(datetime.min.date(), self.start_time)
        dt += timedelta(hours=1)
        return dt.time()
    
    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} {self.start_time.strftime('%I:%M %p')} - {self.end_time().strftime('%I:%M %p')}"

class Waitlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)

class Invoice(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Announcements(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)




