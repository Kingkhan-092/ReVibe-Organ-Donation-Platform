from django.db import models
from hospitals.models import User
from datetime import date, time

# Create your models here.


class DonationRequests(models.Model):
    STATUS = [
        ("Pending", "Pending"),
        ("Not Booked", "Not Booked"),
        ("Booked", "Booked"),
        ("Approved", "Approved"),
        ("Denied", "Denied"),
    ]

    class Meta:
        verbose_name_plural = "Donation Requests"
        verbose_name = "Donation Request"

    organ_type = models.CharField(max_length=20, blank=False, null=False)
    blood_type = models.CharField(max_length=10, blank=True, null=False)
    family_relation = models.CharField(max_length=10, blank=False, null=False)
    family_relation_name = models.CharField(max_length=10, blank=False, null=False)
    family_contact_number = models.CharField(max_length=20, blank=False, null=False)  # Required field
    donation_status = models.CharField(max_length=20, choices=STATUS, blank=False, null=False)
    upload_medical_doc = models.FileField(upload_to='medical_docs/', blank=False, null=False)  # Optional folder for organization
    donated_before = models.BooleanField(blank=False, null=False)
    family_consent = models.BooleanField(blank=False, null=False)
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    request_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor}-{self.organ_type}"





class Appointments(models.Model):
    STATUS = [
        ("Pending", "Pending"),
        ("Not Booked", "Not Booked"),
        ("Booked", "Booked"),
        ("Approved", "Approved"),
        ("Denied", "Denied"),
    ]

    donation_request = models.ForeignKey(DonationRequests, on_delete=models.CASCADE)
    appointment_status = models.CharField(
        max_length=20,
        choices=STATUS,
        blank=False,
        null=False,
        default='Pending'  # Default to 'Pending'
    )
    hospital = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False, default=date.today)  # Default to today's date
    time = models.TimeField(blank=False, null=False, default=time(9, 0))  # Default time is 9:00 AM

    def __str__(self):
        return f"Appointment with {self.donation_request.donor} on {self.date}"

    class Meta:
        verbose_name_plural = "Appointments"
        verbose_name = "Appointment"