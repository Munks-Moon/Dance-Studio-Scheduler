from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Invoice, Waitlist, TimeSlot, Announcements
from django.forms.widgets import SelectDateWidget
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm
import datetime
import calendar

class LoginForm(AuthenticationForm):
    pass

class RegistrationForm(UserCreationForm):
    access_code = forms.CharField(
        label="Access Code",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_access_code(self):
        access_code = self.cleaned_data.get('access_code')

        # Check if the access code is correct, ensures that the public does not register 
        if access_code != settings.ACCESS_CODE:
            raise forms.ValidationError("Invalid access code. Please contact support.")

        return access_code
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = [
            "parent_full_name",
            "parent_email",
            "parent_phone",
            "address",
            "city",
            "province",
            "zip_code",
            "emergency_contact_full_name",
            "emergency_contact_phone",
            "notes",
            "dancer_full_name",
            "dancer_date_of_birth",
            "username",
        ]
        widgets = {
            "password": forms.PasswordInput(),
            "dancer_date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

class TimeSlotApplicationForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["date", "start_time"]

    date = forms.DateField(
        widget=SelectDateWidget(
            empty_label=("Choose Year", "Choose Month", "Choose Day"),
            years=range(2023, 2030),
        )
    )

    def __init__(self, *args, **kwargs):
        super(TimeSlotApplicationForm, self).__init__(*args, **kwargs)
        now = datetime.datetime.now()

        is_weekday = now.weekday() < 5 

        if is_weekday:
            start_time_range = datetime.datetime.combine(
                now.date(), datetime.time(9, 0)
            )  
        else:
            start_time_range = datetime.datetime.combine(
                now.date(), datetime.time(9, 0)
            )  
        end_time_range = datetime.datetime.combine(
            now.date(), datetime.time(22, 0)
        )  

        time_choices = [
            (str(t.time()), t.strftime("%I:%M %p"))
            for t in self.time_range(
                start_time_range, end_time_range, datetime.timedelta(hours=1)
            )
        ]

        self.fields["date"].initial = datetime.date.today()
        self.fields["start_time"].widget = forms.Select(choices=time_choices)

    @staticmethod
    def time_range(start, end, step):
        current_time = start
        while current_time < end:
            yield current_time
            current_time += step

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        date = cleaned_data.get('date')
        current_date = datetime.date.today()

        existing_timeslot = TimeSlot.objects.filter(date=date, start_time=start_time).first()

        if existing_timeslot:
            if existing_timeslot.status != 'canceled':
            # If the timeslot exists and is not canceled, show an error
                waitlist_url = reverse("waitlist-submission")
                waitlist_link = f'<a href="{waitlist_url}">Click here to join the waitlist</a>'
                error_message = mark_safe(f"{waitlist_link}")
                self.add_error(None, error_message)
            else:
            # If the timeslot is canceled, update the instance of the form
                self.instance = existing_timeslot
        
        if date.weekday() < 5:
            if start_time < datetime.time(16, 0):  
                raise ValidationError("Timeslots before 4 PM are not valid on weekdays.")
        
        if date < current_date:
            raise forms.ValidationError("You cannot book a past timeslot.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super(TimeSlotApplicationForm, self).save(commit=False)
        instance.is_available = False
        
        if commit:
            instance.save()
        return instance
    
    def notify_client_unavailability(self, request):
        messages.error(request, "Sorry, the timeslot you've selected is not available.")

class InvoiceForm(forms.ModelForm):

    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]
    CURRENT_YEAR = datetime.date.today().year
    YEAR_CHOICES = [(i, i) for i in range(CURRENT_YEAR - 5, CURRENT_YEAR + 6)]

    month = forms.ChoiceField(choices=MONTH_CHOICES)
    year = forms.ChoiceField(choices=YEAR_CHOICES)

    class Meta:
        model = Invoice
        fields = ['month', 'year']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(InvoiceForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(InvoiceForm, self).save(commit=False)
        instance.client = self.user
        if commit:
            instance.save()
        return instance
    
class WaitlistForm(forms.ModelForm):
    class Meta:
        model = Waitlist
        fields = ["timeslot"]

    def __init__(self, *args, **kwargs):
        super(WaitlistForm, self).__init__(*args, **kwargs)

        self.fields["timeslot"].label = "Select Date and Time"

class EditAccountForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ['username', 'parent_full_name', 'parent_email', 'parent_phone', 
                  'address', 'city', 'province', 'zip_code', 
                  'emergency_contact_full_name', 'emergency_contact_phone', 
                  'notes', 'dancer_full_name', 'dancer_date_of_birth']
        
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcements
        fields = ['title', 'content']