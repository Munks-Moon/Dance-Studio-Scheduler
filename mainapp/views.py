from django.shortcuts import render, redirect
from .forms import LoginForm, TimeSlotApplicationForm, InvoiceForm, WaitlistForm, EditAccountForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import RegistrationForm, AnnouncementForm
from django.contrib import messages
from .models import CustomUser, TimeSlot, Invoice, Waitlist, CanceledTimeSlot, Announcements
from django.shortcuts import get_object_or_404
from datetime import datetime, date, timedelta
from .utils import TimeSlotCalendar
from django.http import JsonResponse
from django.core.paginator import Paginator
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
import calendar
from django.core.mail import EmailMessage
import os
from django.conf import settings
from django.db.models import Count

# Notfication/Announcements ----

def waitlist_notification(timeslot):
    waitlist_entry = Waitlist.objects.filter(timeslot=timeslot).order_by('timestamp').first()

    # Next waitlist user will fill the canceled timeslot automatically
    if waitlist_entry:
        next_user = waitlist_entry.user

        timeslot.client = next_user 
        timeslot.status = "confirmed"
        timeslot.is_new = True  
        timeslot.save()

        subject = f"Timeslot Cancellation: {timeslot.date} {timeslot.start_time}"
        message = f"Dear {next_user.username},\n\nA timeslot on {timeslot.date} at {timeslot.start_time} has become available and has been assigned to you. If this timeslot no longer works for you please cancel as soon as possible.\n\nThank you!"
        recipient_list = [timeslot.client.parent_email]

        em = EmailMessage(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        em.send()
        # The waitlist entry is deleted
        waitlist_entry.delete()
    else:
        timeslot = timeslot
        timeslot.delete()

def announcement_page(request):
    announcements = Announcements.objects.all()
    return render(request, "announcements.html", {'announcements': announcements})

def create_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.save()
            messages.success(request, "Your announcement has been posted!")
            return redirect("dashboard")
    else:
        form = AnnouncementForm()

    return render(request, 'create_announcement.html', {'form': form})

# Dashboard ----

def dashboard(request):
    # Current date allows calendar page to be updated to the corresponding date
    current_date = datetime.now()
    year = current_date.year
    month = current_date.strftime("%B").lower()
    new_timeslot = TimeSlot.objects.filter(is_new=True)
    context = {"year": year, "month": month, 'new_timeslot': new_timeslot}
    return render(request, "dashboard.html", context)

# Login/Logout ----

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("dashboard")
                else:
                    return HttpResponse("Disabled account")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})

def logout(request):
    logout(request)
    return redirect("login")

# Registration ----

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration was successful. Please login")
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})

# Account ----

def account(request):
    current_user = request.user
    timeslots = TimeSlot.objects.filter(client=request.user)
    user_waitlist_entries = Waitlist.objects.filter(user=request.user)

    items_per_page = 5

    paginator_timeslots = Paginator(timeslots, items_per_page)
    page_confirmed = request.GET.get("page_confirmed")
    timeslots = paginator_timeslots.get_page(page_confirmed)

    waitlist_positions = []

    for entry in user_waitlist_entries:
        # Retrieve all waitlist entries for the timeslot associated with this entry
        all_entries_for_timeslot = Waitlist.objects.filter(timeslot=entry.timeslot).order_by('timestamp')
        
        # Find the user's position
        position = list(all_entries_for_timeslot).index(entry) + 1
        waitlist_positions.append((entry, position))

    context = {
        "current_user": current_user,
        "timeslots": timeslots,  
        "waitlist_positions": waitlist_positions,
    }

    return render(request, "account.html", context)

def edit_account(request):
    if request.method == 'POST':
        form = EditAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account was successfully updated!')
            return redirect('account')
    else:
        form = EditAccountForm(instance=request.user)
    
    return render(request, 'edit_account.html', {'form': form})

def calendar_view(request, year=date.today().year, month=date.today().month):
    month_number = datetime.strptime(month, "%B").month
    current_month = datetime(year, month_number, 1)
    next_month = current_month + timedelta(
        days=31
    )  
    prev_month = current_month - timedelta(days=1)

    if isinstance(month, str):
        try:
            datetime_object = datetime.strptime(month, "%B")
            month = datetime_object.month
        except ValueError:
            return HttpResponse("Invalid month name")

    time_slots = TimeSlot.objects.filter(date__year=year, date__month=month, status='confirmed')
    cal = (
        TimeSlotCalendar(time_slots, request.user)
        .formatmonth(year, month)
        .replace("<table", '<table class="calendar"')
    )

    return render(
        request,
        "calendar.html",
        {
            "cal": cal,
            "next_month": next_month.strftime("%B"),
            "next_year": next_month.year,
            "prev_month": prev_month.strftime("%B"),
            "prev_year": prev_month.year,
        },
    )

# Timeslots ----

def send_confirmation_email(receiver_email, timeslot):
    subject = "Timeslot Application Confirmation"
    body = (
        f"Dear {timeslot.client.username},\n\n"
        f"Thank you for applying for a timeslot. Your application for {timeslot.date} at {timeslot.start_time} has been received.\n\n"
        "Best regards,\n"
        "Your Team"
    )

    em = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [receiver_email])

    em.send()

def apply_for_timeslot(request):
    if request.method == "POST":
        form = TimeSlotApplicationForm(request.POST)
        if form.is_valid():
            form.instance.client = request.user
            timeslot = form.save(commit=False)
            timeslot.save()

            send_confirmation_email(timeslot.client.parent_email, timeslot)
            messages.success(
                request, "Your timeslot application has been successfully submitted!"
            )
            return redirect("dashboard")
    else:
        form = TimeSlotApplicationForm()

    return render(request, "timeslot_submission.html", {"form": form})

def apply_for_timeslot_link(request, date): # Calendar
    if request.method == "POST":
        form = TimeSlotApplicationForm(request.POST)
        if form.is_valid():
            form.instance.client = request.user
            timeslot = form.save(commit=False)
            timeslot.save()

            send_confirmation_email(timeslot.client.parent_email, timeslot)
            messages.success(
                request, "Your timeslot application has been successfully submitted!"
            )

            return redirect("dashboard")
    else:
        form = TimeSlotApplicationForm(initial={"date": date})

    return render(request, "timeslot_submission.html", {"form": form})

def confirm_cancellation(request, pk):
    timeslot = get_object_or_404(TimeSlot, id=pk)

    canceled_timeslot = CanceledTimeSlot(date=timeslot.date, start_time=timeslot.start_time, client=timeslot.client)

    canceled_timeslot.save()

    waitlist_notification(timeslot)

    messages.success(request, "Timeslot has been successfully canceled.")
    return redirect('dashboard')

def cancel_timeslot(request, pk):
    timeslot = get_object_or_404(TimeSlot, id=pk)
    return render(request, 'cancel_timeslot.html', {'timeslot': timeslot})

# Waitlist ----

def join_waitlist(request):
    if request.method == "POST":
        form = WaitlistForm(request.POST)
        if form.is_valid():
            waitlist_entry = form.save(commit=False)
            waitlist_entry.user = request.user
            waitlist_entry.save()
            messages.success(
                request, "You have been successfully added to the waitlist"
            )
            return redirect(
                "dashboard"
            )  

    else:
        form = WaitlistForm()

    return render(request, "waitlist_submission.html", {"form": form})

# Admin Only ----

def user_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_timeslots = TimeSlot.objects.filter(client=user)
    invoices = Invoice.objects.filter(client=user).order_by("-created_at")

    items_per_page = 5

    paginator_confirmed = Paginator(user_timeslots, items_per_page)
    page_confirmed = request.GET.get("page_confirmed")
    user_timeslots = paginator_confirmed.get_page(page_confirmed)

    context = {"user": user, "user_timeslots": user_timeslots, "invoices": invoices}

    return render(request, "admin/user_profile.html", context)

def client_list(request):
    superuser = CustomUser.objects.filter(is_superuser=True)
    clients = CustomUser.objects.all().order_by("username").exclude(id__in=superuser.values_list('id', flat=True))
    return render(request, "admin/client_list.html", {"clients": clients})

def timeslot_bookings(request):
    # Organization of new, confirmed, and canceled timeslots for display
    items_per_page = 8

    confirmed_timeslots_list = TimeSlot.objects.filter(status="confirmed").order_by(
        "date"
    )
    paginator_confirmed = Paginator(confirmed_timeslots_list, items_per_page)
    page_confirmed = request.GET.get("page_confirmed")
    confirmed_timeslots = paginator_confirmed.get_page(page_confirmed)

    canceled_timeslots_list = CanceledTimeSlot.objects.filter().order_by(
        "date"
    )
    paginator_canceled = Paginator(canceled_timeslots_list, items_per_page)
    page_canceled = request.GET.get("page_canceled")
    canceled_timeslots = paginator_canceled.get_page(page_canceled)

    new_timeslots_list = TimeSlot.objects.filter(status="confirmed", is_new=True)
    paginator_new = Paginator(new_timeslots_list, items_per_page)
    page_new = request.GET.get("page_new")
    new_timeslots = paginator_new.get_page(page_new)

    completed_timeslots_list = TimeSlot.objects.filter(status="completed")
    paginator_completed = Paginator(completed_timeslots_list, items_per_page)
    page_completed = request.GET.get("page_completed")
    completed_timeslots = paginator_completed.get_page(page_completed)

    context = {
        "confirmed_timeslots": confirmed_timeslots,
        "canceled_timeslots": canceled_timeslots,
        "new_timeslots": new_timeslots,
        "completed_timeslots": completed_timeslots
    }
    return render(request, "admin/timeslot_bookings.html", context)

def dismiss_notification(request, timeslot_id):
    timeslot = TimeSlot.objects.get(pk=timeslot_id)
    if request.method == "POST":
        timeslot.is_new = False
        timeslot.save()
        return JsonResponse({"status": "success"})
    
def create_invoice(request, user_id=None):
    client = None
    if user_id:
        client = CustomUser.objects.get(pk=user_id)

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            client = CustomUser.objects.get(pk=user_id)
            month = form.cleaned_data["month"]
            year = form.cleaned_data["year"]

            timeslots = TimeSlot.objects.filter(
                client=client, date__month=month, date__year=year
            )

            invoice = Invoice(
                client=client, month=month, year=year, total_amount=len(timeslots) * 40
            )
            invoice.save()

            # Generate the invoice PDF
            template = get_template("invoice.html")
            month_name = calendar.month_name[int(month)]
            context = {
                "invoice": invoice,  
                "client": client,
                "timeslots": timeslots,
                "month": month_name,
                "year": year,
                "total_cost": len(timeslots)
                * 40,  
            }
            html = template.render(context)
            pdf_file = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=pdf_file)
            if pisa_status.err:
                return HttpResponse("We had some errors <pre>" + html + "</pre>")

            # Save the generated PDF to the Invoice instance
            invoice.pdf_file.save(
                f"invoice_{client.username}_{month}_{year}.pdf", pdf_file
            )
            invoice.save()

            return redirect(
                "user-profile", user_id=client.id
            )

    else:
        form = InvoiceForm(initial={"client": user_id})

    return render(request, "admin/create_invoice.html", {"form": form})


def send_invoice_email(request, user_id):
    if request.method == "POST":
        invoice_id = request.POST.get("invoice_id")
        invoice = get_object_or_404(Invoice, id=invoice_id)
        user = get_object_or_404(CustomUser, id=user_id)

        receiver = user.parent_email 
        subject = f"Invoice for {invoice.month}/{invoice.year}"
        body = f"Dear {user.username},\n\nPlease find attached the invoice for {invoice.month}/{invoice.year}."

        em = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [receiver])

        filename = f"invoice_{user.username}_{invoice.month}_{invoice.year}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, "invoices", filename)

        with open(filepath, "rb") as attachment:
            em.attach(filename, attachment.read(), "application/pdf")

        em.send()

    return redirect("dashboard")

def fetch_timeslots_for_month(user, year, month):
    return TimeSlot.objects.filter(client=user, date__year=year, date__month=month)

# Waitlist ----

def waitlist(request):
    waitlist = TimeSlot.objects.annotate(waitlist_count=Count('waitlist')).filter(waitlist_count__gt=0)
    return render(request, "admin/waitlist.html", {"waitlist": waitlist})

def waitlist_timeslot(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, pk=timeslot_id)
    waitlist = timeslot.waitlist_set.all()

    context = {
        'timeslot': timeslot,
        'waitlist': waitlist,
    }

    return render(request, 'admin/waitlist_timeslot.html', context)

def cancel_waitlist(request, waitlist_id):
    waitlist_entry = get_object_or_404(Waitlist, pk=waitlist_id)

    if request.method == "POST":
        if waitlist_entry.user == request.user:
            waitlist_entry.delete()
            messages.success(request, "You have successfully canceled your waitlist entry.")
            return redirect('dashboard')
        else:
            messages.error(request, "You are not authorized to cancel this waitlist entry.")
    return render(request, 'cancel_waitlist.html', {'waitlist_entry': waitlist_entry})
    

