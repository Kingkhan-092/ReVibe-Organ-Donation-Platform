from django.urls import path
from django.urls import re_path
from donors.views import get_pending_appointments
from .views import UpdateAppointmentStatusView


from . import views

urlpatterns = [
    re_path('register/$', views.donor_register, name='donor-register'),
    re_path('login/$', views.donor_login, name='donor-login'),
    re_path('update_profile/$', views.donor_profile_update, name="donor-profile-update"),
    re_path('donation-history/$', views.donor_home, name='donor-home'),
    re_path('forgot-password/$', views.donor_forgot_password, name='donor-forgot-password'),
    re_path('logout/$', views.donor_logout, name="donor-logout"),
    re_path('new-donation-request/$', views.new_donation_request, name='new-donation-request'),
    re_path('book-appointment/$', views.book_appointment, name='book-appointment'),
    re_path('home/$', views.donor_landing_page, name="donor-landing-page"),
    re_path('select-date/', views.date_view, name='select_date'),
    re_path('api/pending-appointments/', get_pending_appointments, name='pending-appointments'),
    re_path('api/update-appointment-status/<int:appointment_id>/', UpdateAppointmentStatusView.as_view(), name='update_appointment_status'),
]