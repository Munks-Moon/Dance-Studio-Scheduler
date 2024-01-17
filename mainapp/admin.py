from django.contrib import admin
from .models import CustomUser, TimeSlot, Invoice, Waitlist, CanceledTimeSlot, Announcements
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'parent_full_name', 'parent_email', 'parent_phone', 
                  'address', 'city', 'province', 'zip_code', 
                  'emergency_contact_full_name', 'emergency_contact_phone', 
                  'notes', 'dancer_full_name', 'dancer_date_of_birth']
    
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'client']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['client', 'month']

@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'timeslot']

@admin.register(CanceledTimeSlot)
class CanceledTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'client']

admin.site.register(Announcements)
class AnnouncementsAdmin(admin.ModelAdmin):
    list_display = ['title', 'content']