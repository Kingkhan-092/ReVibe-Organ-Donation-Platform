from django.shortcuts import render, redirect
from hospitals.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import smtplib
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import string
import secrets
import ast
import random
from .models import DonationRequests, Appointments
from django.http import HttpResponse
from datetime import date, timedelta

from django.contrib import messages
from django.utils import timezone


# Create your views here.
#@login_required(login_url="donor-login")
def donor_register(request):

    # If method is post
    if request.POST:
        user = User()
        user.username = request.POST.get("username", "")
        user.set_password(request.POST.get("password", ""))
        user.email = request.POST.get("email", "")
        user.first_name = request.POST.get("donor_name", "")
        user.city = request.POST.get("city", "")
        user.province = request.POST.get("province", "")
        user.country = request.POST.get("country", "")
        user.contact_number = request.POST.get("contact_number", "")
        user.is_staff = False
        user.save()
        return redirect('donor-login')

    return render(request, "donor-registration.html")

def donor_login(request):
    # If method is post
    if request.POST:
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if not user.is_staff:
                    login(request, user)
                    print(request.user, "helo")
                    return redirect(request.POST.get("next", "donor-landing-page"))
        else:
            msg = "Invalid password"
            fail = 1
            return render(request, "donor-login.html", {"fail": fail, "msg": msg})

    return render(request, "donor-login.html")


def donor_profile_update(request):
    success = 0
    msg = 0
    pfcheck = 0
    pscheck = 0
    if "profile" in request.POST:
        user = User.objects.get(id=request.user.id)
        user.email = request.POST.get("email", "")
        user.first_name = request.POST.get("donor_name", "")
        user.city = request.POST.get("city", "")
        user.province = request.POST.get("province", "")
        user.contact_number = request.POST.get("contact", "")
        user.save()
        success = 1
        pfcheck = 1
        msg = "User Profile Updated!"
    elif "password" in request.POST:
        user = authenticate(username=request.user.username, password=request.POST.get("old_password", ""))
        if user is not None:
            user.set_password(request.POST.get("new_password", ""))
            user.save()
            success = 1
            pscheck = 1
            msg = "Password changed!"
        else:
            success = 1
            pscheck = 1
            msg = "Invalid password"
    
    donor = User.objects.get(id=request.user.id)
    
    # Updated list of states (provinces) in India
    provinces = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
        "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
        "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
        "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    
    # Updated list of countries
    countries = [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", 
        "Brunei", "Cambodia", "China", "Cyprus", "Georgia", "India", "Indonesia", 
        "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", 
        "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia", "Myanmar (Burma)", "Nepal", 
        "North Korea", "Oman", "Pakistan", "Palestine", "Philippines", "Qatar", "Saudi Arabia", 
        "Singapore", "South Korea", "Sri Lanka", "Syria", "Taiwan", "Tajikistan", "Thailand", 
        "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", 
        "Yemen"
    ]
    
    # Update the province and country selection status
    provinces = [1 if donor.province == province else 0 for province in provinces]
    
    return render(request, "donor-profile-update.html", {
        "provinces": provinces, 
        "countries": countries,  # Pass the countries list to the template
        "donor": donor, 
        "success": success, 
        "msg": msg,
        "pfcheck": pfcheck, 
        "pscheck": pscheck
    })


def send_mail(send_from, send_to, subject, body_of_msg, files=[],
              server="localhost", port=587, username='', password='',
              use_tls=True):
    message = MIMEMultipart()
    message['From'] = send_from
    message['To'] = send_to
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message.attach(MIMEText(body_of_msg))
    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, message.as_string())
    smtp.quit()


def donor_forgot_password(request):
    success = 0
    if request.POST:
        username = request.POST.get("username", "")
        try:
            user = User.objects.get(username=username)
            email = user.email
            password = random.randint(1000000, 999999999999)
            send_mail("foodatdalteam@gmail.com", email, "Password reset for your organ donation account",
                      """Your request to change password has been processed.\nThis is your new password: {}\n
                            If you wish to change password, please go to your user profile and change it.""".format(password),
                      server="smtp.gmail.com", username="foodatdalteam@gmail.com", password="foodatdal")
            user.set_password(password)
            user.save()
            success = 1
            msg = "Success. Check your registered email for new password!"
            return render(request, "donor-forgot-password.html", {"success": success, "msg": msg})
        except:
            success = 1
            msg = "User does not exist!"
            return render(request, "donor-forgot-password.html", {"success": success, "msg": msg})

    return render(request, "donor-forgot-password.html", {"success": success})


def donor_logout(request):
    logout(request)
    return redirect("donor-login")


def donor_landing_page(request):
    return render(request, "donor_landing_page.html")


def donor_home(request):
    donor_requests = DonationRequests.objects.filter(donor=request.user)
    for donor_request in donor_requests:
        try:
            donor_request.datetime = donor_request.request_datetime.strftime("%b %d, %Y %H:%M:%S")
            status = Appointments.objects.get(donation_request=donor_request).appointment_status
        except Exception as e:
            status = "Not Booked"
        donor_request.appointment_status = status
    return render(request, "donor-home.html", {"donationrequests": donor_requests})


def new_donation_request(request):
    if request.method == "POST":
        donation_request = DonationRequests()
        donation_request.donation_request = request.POST.get("newdonationreq", "")
        donation_request.organ_type = request.POST.get("organ_type", "")
        donation_request.blood_type = request.POST.get("blood_type", "")
        donation_request.family_relation = request.POST.get("family_relation", "")
        donation_request.family_relation_name = request.POST.get("family_relation_name", "")
        donation_request.family_contact_number = request.POST.get("family_contact_number", "")
        donation_request.donation_status = "Pending"
        donation_request.donor = request.user
        donation_request.upload_medical_doc = request.FILES.get("file")  # This is fine
        donation_request.family_consent = request.POST.get("family_consent", "")
        donation_request.donated_before = request.POST.get("donated_before", "")
        donation_request.save()
        return redirect("donor-home")

    return render(request, "new-donation-request.html")





def book_appointment(request):
    donors = DonationRequests.objects.filter(donor=request.user.id).exclude(donation_status='Denied')
    users = User.objects.filter(is_staff=True)
    today = timezone.now().date()
    max_date = (timezone.now() + timezone.timedelta(days=60)).date()
    time_slots = [
        "8:00 to 9:00", "9:00 to 10:00", "10:00 to 11:00", "12:00 to 13:00",
        "13:00 to 14:00", "14:00 to 15:00", "15:00 to 16:00", "16:00 to 17:00",
        "17:00 to 18:00", "18:00 to 19:00"
    ]

    if request.method == "POST":
        dreq_id = request.POST.get("dreq")
        hospital_name = request.POST.get("hospital-name")
        date = request.POST.get("date")
        time = request.POST.get("time")

        print("POST data:", request.POST)

        errors = []

        if not dreq_id:
            errors.append("Donation request is required.")
        if not hospital_name or hospital_name == "None":
            errors.append("Hospital name is required.")
        if not date:
            errors.append("Appointment date is required.")
        if not time:
            errors.append("Preferred time is required.")

        if errors:
            return render(request, "book-appointment.html", {
                "donors": donors,
                "users": users,
                "errors": errors,
                "today": today,
                "max_date": max_date,
                "time_slots": time_slots
            })

        try:
            # Extract the start time from the time string
            start_time_str = time.split(" to ")[0]  # Extract "13:00" from "13:00 to 14:00"
            
            # Convert to a datetime object (if needed, though this is optional if using only hours and minutes)
            start_time = timezone.datetime.strptime(start_time_str, "%H:%M").time()

            # Look up the donation request
            donation_request = DonationRequests.objects.get(id=int(dreq_id))

            # Look up the hospital user
            hospital_user = User.objects.get(hospital_name=hospital_name)

            # Create and save the appointment
            apmt = Appointments(
                donation_request=donation_request,
                hospital=hospital_user,
                date=date,
                time=start_time,  # Save the extracted start time
                appointment_status="Pending"
            )
            apmt.save()

            messages.success(request, "Appointment booked successfully!")
            return redirect("donor-home")

        except DonationRequests.DoesNotExist:
            errors.append("Invalid donation request selected.")
        except User.DoesNotExist:
            errors.append("Selected hospital not found.")
        except Exception as e:
            errors.append(f"Unexpected error: {e}")

        return render(request, "book-appointment.html", {
            "donors": donors,
            "users": users,
            "errors": errors,
            "today": today,
            "max_date": max_date,
            "time_slots": time_slots
        })

    # GET request - initial page load
    return render(request, "book-appointment.html", {
        "donors": donors,
        "users": users,
        "today": today,
        "max_date": max_date,
        "time_slots": time_slots
    })


def wedonate(request):
    if request.POST:
        pass
    return render(request, "index.html")

def about_us(request):
    return render(request, 'about-us.html')

def community(request):
    return render(request, 'community.html')

def date_view(request):
    today = date.today()
    max_date = today + timedelta(days=60)
    context = {
        'today': today.isoformat(),
        'max_date': max_date.isoformat()
    }
    return render(request, 'date_picker.html', context)


def dashboard(request):
    pending_appointments = Appointments.objects.filter(status='pending').count()
    pending_donations = DonationRequests.objects.filter(status='pending').count()

    context = {
        'pending_appointments': pending_appointments,
        'pending_donations': pending_donations,
    }

    return render(request, 'dashboard.html', context)

from django.http import JsonResponse
from donors.models import Appointments

def get_pending_appointments(request):
    pending_appointments = Appointments.objects.filter(appointment_status='Pending').select_related(
        'donation_request__donor'
    )

    data = []
    for appointment in pending_appointments:
        donor = appointment.donation_request.donor
        data.append({
            'appointment_id': appointment.id,
            'donor_name': donor.first_name + ' ' + donor.last_name,
            'organ': appointment.donation_request.organ_type,
            'appointment_date': appointment.date.strftime('%Y-%m-%d'),
            'appointment_time': appointment.time.strftime('%H:%M'),
        })

    return JsonResponse(data, safe=False)

from django.views import View
import json
from django.utils.decorators import method_decorator

class UpdateAppointmentStatusView(View):
    def post(self, request, appointment_id):
        try:
            data = json.loads(request.body)
            new_status = data.get('status')

            if new_status not in ['Approved', 'Denied']:
                return JsonResponse({'error': 'Invalid status'}, status=400)

            appointment = Appointments.objects.get(id=appointment_id)
            appointment.appointment_status = new_status
            appointment.save()

            return JsonResponse({'success': True, 'status': new_status})

        except Appointments.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)