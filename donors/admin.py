# donors/admin.py
from django.contrib import admin
from .models import DonationRequests, Appointments

# DonationRequests Admin Configuration
class DonationRequestsAdmin(admin.ModelAdmin):
    list_display = ('donor', 'organ_type', 'donation_status', 'request_datetime', 'blood_type', 'family_contact_number')
    search_fields = ['donor__username', 'organ_type', 'donation_status']
    list_filter = ['donation_status', 'donor']
    ordering = ['request_datetime']
    date_hierarchy = 'request_datetime'

admin.site.register(DonationRequests, DonationRequestsAdmin)

# Appointments Admin Configuration
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ('donation_request', 'hospital', 'date', 'time', 'appointment_status')
    search_fields = ['donation_request__donor__username', 'hospital__hospital_name']
    list_filter = ['appointment_status', 'hospital', 'date']
    ordering = ['date']
    date_hierarchy = 'date'

admin.site.register(Appointments, AppointmentsAdmin)
