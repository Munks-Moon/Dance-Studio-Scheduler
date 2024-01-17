from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("user_profile/<int:user_id>/", views.user_profile, name="user-profile"),
    path("client_list/", views.client_list, name="client-list"),
    path("<int:year>/<str:month>", views.calendar_view, name="calendar"),
    path("timeslot/", views.apply_for_timeslot, name="timeslot"),
    path('waitlist_submission/', views.join_waitlist, name='waitlist-submission'),
    path('waitlist/', views.waitlist, name='waitlist'),
    path('waitlist/<int:timeslot_id>/', views.waitlist_timeslot, name='waitlist_timeslot'),
    path('cancel_waitlist/<int:waitlist_id>/', views.cancel_waitlist, name='cancel-waitlist'),
    path(
        "timeslot/<str:date>/",
        views.apply_for_timeslot_link,
        name="timeslot-calendar-link",
    ),
    path("timeslot_bookings/", views.timeslot_bookings, name="timeslot-bookings"),
    path("timeslot/cancel/<str:pk>/", views.cancel_timeslot, name="cancel-timeslot"),
    path("timeslot/confirm_cancel/<str:pk>/", views.confirm_cancellation, name="confirm_cancellation"),
    path(
        "dismiss_notification/<int:timeslot_id>/",
        views.dismiss_notification,
        name="dismiss_notification",
    ),
    path(
        "create-invoice/<int:user_id>/",
        views.create_invoice,
        name="create_invoice_for_user",
    ),
    path(
        "send-invoice-email/<int:user_id>/",
        views.send_invoice_email,
        name="send_invoice_email",
    ),
    path('edit_account/', views.edit_account, name='edit-account'),
    path('announcements/', views.announcement_page, name='announcements'),
    path('create_announcement', views.create_announcement, name='create-announcement'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password-reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password-reset-complete'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
