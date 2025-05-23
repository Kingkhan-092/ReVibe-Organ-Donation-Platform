from django.shortcuts import render
import pdfkit
from django.conf import settings
from django.db.models import Q
from donors.models import DonationRequests, Appointments
import json
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_protect
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
from donors.models import DonationRequests, Appointments
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import StringIO, BytesIO
from xhtml2pdf import pisa
from PyPDF2 import PdfFileMerger, PdfFileReader
from django.views.decorators.http import require_POST


# Create your views here.


def home(request):
    if request.POST:
        pass
    return render(request, "hospital-main-page.html")


def search_donations(request):
    if request.POST:
        pass
    else:
        search_keyword = request.GET.get('keyword', '')
        status = "Approved"
        # Search for donations based on organ type/blood type/donor name
        donations = DonationRequests.objects.filter((Q(organ_type__iexact=search_keyword) | Q(blood_type__startswith=search_keyword) | Q(donor__first_name__iexact=search_keyword) | Q(donor__last_name__iexact=search_keyword)) & Q(donation_status__iexact=status))
        print(donations)
        # Search for donations based on donation id
        if not donations:
            if search_keyword.isdigit():
                donations = DonationRequests.objects.filter(Q(id=int(search_keyword)) & Q(donation_status__iexact=status))

        donation_list = []
        for donation in donations:
            print(donation.donation_status)
            temp_dict = {}
            temp_dict["donor"] = f"{donation.donor.first_name} {donation.donor.last_name}"
            temp_dict["organ"] = donation.organ_type
            temp_dict["donation_id"] = donation.id
            temp_dict["blood_group"] = donation.blood_type
            donation_list.append(temp_dict)
        search_list = json.dumps(donation_list)
        print("hi", search_list)
        return HttpResponse(search_list)


def search_donation_details(request):
    if request.POST:
        pass
    else:
        # Fetching donation details
        donation_id_from_UI = request.GET.get('donation_id', '')
        donations = Appointments.objects.filter(Q(donation_request__id=int(donation_id_from_UI)))
        donation_list = []
        for donation in donations:
            temp_dict = {}
            # Donor details
            temp_dict["user_name"] = donation.donation_request.donor.username
            temp_dict["first_name"] = donation.donation_request.donor.first_name
            temp_dict["last_name"] = donation.donation_request.donor.last_name
            temp_dict["email"] = donation.donation_request.donor.email
            temp_dict["contact_number"] = donation.donation_request.donor.contact_number
            temp_dict["city"] = donation.donation_request.donor.city
            temp_dict["country"] = donation.donation_request.donor.country
            temp_dict["province"] = donation.donation_request.donor.province
            # Donation details
            temp_dict["organ"] = donation.donation_request.organ_type
            temp_dict["donation_id"] = donation.donation_request.id
            temp_dict["blood_group"] = donation.donation_request.blood_type
            temp_dict["donation_status"] = donation.donation_request.donation_status
            temp_dict["approved_by"] = donation.hospital.hospital_name
            temp_dict["family_member_name"] = donation.donation_request.family_relation_name
            temp_dict["family_member_relation"] = donation.donation_request.family_relation
            temp_dict["family_member_contact"] = donation.donation_request.family_contact_number
            donation_list.append(temp_dict)
        donation_details = json.dumps(donation_list)

        return HttpResponse(donation_details)


def fetch_appointments(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    appointments = Appointments.objects.filter(
        hospital=request.user,
        appointment_status="Pending"
    ).select_related('donation_request__donor')
    
    data = [{
        'id': app.id,
        'donor_name': f"{app.donation_request.donor.first_name} {app.donation_request.donor.last_name}",
        'organ': app.donation_request.organ_type,
        'date': app.date.strftime('%Y-%m-%d'),
        'time': app.time.strftime('%H:%M'),
        'status': app.appointment_status
    } for app in appointments]
    
    return JsonResponse({'appointments': data})

def fetch_donations(request):
    """Fetch pending donations for approved appointments"""
    donation_status = "Pending"
    appointment_status = "Approved"
    
    appointments = Appointments.objects.filter(
        Q(hospital__id=request.user.id) & 
        Q(appointment_status=appointment_status) & 
        Q(donation_request__donation_status=donation_status)
    ).select_related('donation_request', 'donation_request__donor')
    
    donation_list = []
    for appointment in appointments:
        donation_list.append({
            "first_name": appointment.donation_request.donor.first_name,
            "last_name": appointment.donation_request.donor.last_name,
            "organ": appointment.donation_request.organ_type,
            "donation_id": appointment.donation_request.id,
            "blood_group": appointment.donation_request.blood_type,
            "appointment_id": appointment.id,
            "date": appointment.date.strftime("%Y-%m-%d") if appointment.date else None,
            "time": appointment.time.strftime("%H:%M") if appointment.time else None,
            "appointment_status": appointment.appointment_status
        })
    
    return JsonResponse({"data": donation_list})

def hospital_register(request):
    if request.POST:
        user = User()

        # Ensure hospital_name is assigned correctly
        user.hospital_name = request.POST.get("hospital_name", "").strip()

        # other fields...
        user.username = request.POST.get("username", "").strip()
        user.set_password(request.POST.get("password", ""))
        user.email = request.POST.get("email", "").strip()
        user.city = request.POST.get("city", "").strip()
        user.province = request.POST.get("province", "").strip()
        user.country = request.POST.get("country", "").strip()
        user.contact_number = request.POST.get("contact_number", "").strip()

        user.is_staff = True  # mark as hospital staff
        user.save()

        return redirect('hospital-login')

    return render(request, "hospital-registration.html")



# Login view for hospital users
def hospital_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                if user.is_staff:  # Ensure only staff users can login
                    login(request, user)
                    # Redirect to hospital main page (or dashboard)
                    return redirect("hospital-main-page")  # Change to your main page route
                else:
                    msg = "You are not authorized to access the hospital portal."
                    return render(request, "hospital-login.html", {"msg": msg})
            else:
                msg = "User account is inactive."
                return render(request, "hospital-login.html", {"msg": msg})
        else:
            msg = "Invalid username or password."
            return render(request, "hospital-login.html", {"msg": msg})

    return render(request, "hospital-login.html")

# Add a hospital main page view for after successful login
@login_required
def hospital_main_page(request):
    return render(request, "hospital-main-page.html")  # Ensure this template exists


def fetch_appointment_details(request):
    if request.POST:
        pass
    else:
        # Fetching appointment details
        appointment_id_from_UI = request.GET.get('appointment_id', '')
        print('appointment id', appointment_id_from_UI)
        appointments = Appointments.objects.filter(Q(id=int(appointment_id_from_UI)))
        appointment_list = []
        for appointment in appointments:
            # Donor details
            temp_dict = {}
            temp_dict["first_name"] = appointment.donation_request.donor.first_name
            temp_dict["last_name"] = appointment.donation_request.donor.last_name
            temp_dict["email"] = appointment.donation_request.donor.email
            temp_dict["contact_number"] = appointment.donation_request.donor.contact_number
            temp_dict["city"] = appointment.donation_request.donor.city
            temp_dict["country"] = appointment.donation_request.donor.country
            temp_dict["province"] = appointment.donation_request.donor.province
            # Donation details
            temp_dict["organ"] = appointment.donation_request.organ_type
            temp_dict["donation_id"] = appointment.donation_request.id
            temp_dict["blood_group"] = appointment.donation_request.blood_type
            temp_dict["donation_status"] = appointment.donation_request.donation_status
            temp_dict["family_member_name"] = appointment.donation_request.family_relation_name
            temp_dict["family_member_relation"] = appointment.donation_request.family_relation
            temp_dict["family_member_contact"] = appointment.donation_request.family_contact_number
            # Appointment details
            temp_dict["appointment_id"] = appointment.id
            temp_dict["date"] = appointment.date
            temp_dict["time"] = appointment.time
            temp_dict["appointment_status"] = appointment.appointment_status
            appointment_list.append(temp_dict)
        appointment_details = json.dumps(appointment_list)
        return HttpResponse(appointment_details)


def fetch_donation_details(request):
    if request.POST:
        pass
    else:
        # Fetching donation details
        donation_id_from_UI = request.GET.get('donation_id', '')
        print('donation id', donation_id_from_UI)
        donations = DonationRequests.objects.filter(Q(id=int(donation_id_from_UI)))
        donation_list = []
        for donation in donations:
            # Donor details
            temp_dict = {}
            temp_dict["first_name"] = donation.donor.first_name
            temp_dict["last_name"] = donation.donor.last_name
            temp_dict["email"] = donation.donor.email
            temp_dict["contact_number"] = donation.donor.contact_number
            temp_dict["city"] = donation.donor.city
            temp_dict["country"] = donation.donor.country
            temp_dict["province"] = donation.donor.province
            # Donation details
            temp_dict["organ"] = donation.organ_type
            temp_dict["donation_id"] = donation.id
            temp_dict["blood_group"] = donation.blood_type
            temp_dict["donation_status"] = donation.donation_status
            temp_dict["family_member_name"] = donation.family_relation_name
            temp_dict["family_member_relation"] = donation.family_relation
            temp_dict["family_member_contact"] = donation.family_contact_number

            donation_list.append(temp_dict)
        donation_details = json.dumps(donation_list)
        return HttpResponse(donation_details)

@require_POST
@csrf_exempt
def approve_appointments(request):
    if request.method == "POST":
        try:
            appointment_id = request.POST.get('ID', '')
            action = request.POST.get('action', '')
            appointment = Appointments.objects.get(id=appointment_id)
            appointment.appointment_status = action
            appointment.save()
            return JsonResponse({"status": "success", "message": "Appointment updated!"})
        except Appointments.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Appointment not found!"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

@csrf_exempt
def approve_donations(request):
    if request.POST:
        donation_id_from_UI = request.POST.get('ID', '')
        actionToPerform = request.POST.get('action', '')
        print('donation id', donation_id_from_UI)
        print('actionToPerform', actionToPerform)
        donation = get_object_or_404(DonationRequests, id=donation_id_from_UI)
        donation.donation_status = actionToPerform
        donation.save(update_fields=["donation_status"])
        return JsonResponse({"status": "success"})


def fetch_counts(request):
    if request.POST:
        pass
    else:
        print(request.user.hospital_name)
        appointment_count = Appointments.objects.filter(Q(hospital__hospital_name__iexact=request.user.hospital_name) & Q(appointment_status__iexact="Pending")).count()
        print("appointment count", appointment_count)
        donation_status = "Pending"
        appointment_status = "Approved"
        donation_count = Appointments.objects.filter(Q(hospital__hospital_name__iexact=request.user.hospital_name) & Q(appointment_status__iexact=appointment_status) & Q(donation_request__donation_status__iexact=donation_status)).count()
        print("donation count", donation_count)
        dummy_list = []
        temp_dict = {}
        temp_dict["appointment_count"] = appointment_count
        temp_dict["donation_count"] = donation_count
        dummy_list.append(temp_dict)
        count_json = json.dumps(dummy_list)
        return HttpResponse(count_json)


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


def hospital_forgot_password(request):
    success = 0
    if request.POST:
        username = request.POST.get("username", "")
        try:
            user = User.objects.get(username=username)
            email = user.email
            password = random.randint(1000000, 999999999999)
            user.set_password(password)
            user.save()
            send_mail("foodatdalteam@gmail.com", email, "Password reset for your organ donation account",
                      """Your request to change password has been processed.\nThis is your new password: {}\n
                            If you wish to change password, please go to your user profile and change it.""".format(password),
                      server="smtp.gmail.com", username="foodatdalteam@gmail.com", password="foodatdal")
            success = 1
            msg = "Success. Check your registered email for new password!"
            return render(request, "hospital-forgot-password.html", {"success": success, "msg": msg})
        except:
            success = 1
            msg = "User does not exist!"
            return render(request, "hospital-forgot-password.html", {"success": success, "msg": msg})

    return render(request, "hospital-forgot-password.html", {"success": success})


def form_to_PDF(request, donor_id=1):

    donation_request = DonationRequests.objects.get(id=donor_id)
    user = donation_request.donor
    donations = DonationRequests.objects.filter(donor=user)
    template = get_template("user-details.html")
    html = template.render({'user': user, 'donors': donations})
    config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF)
    try:
        pdf = pdfkit.from_string(html, False, configuration=config)
    except Exception as e:
        print(e)
        pass
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report.pdf"'
    userpdf = PdfFileReader(BytesIO(pdf))
    usermedicaldoc = donation_request.upload_medical_doc.read()
    usermedbytes = BytesIO(usermedicaldoc)
    usermedicalpdf = PdfFileReader(usermedbytes)
    merger = PdfFileMerger()
    merger.append(userpdf)
    merger.append(usermedicalpdf)
    merger.write(response)
    return response


def email_donor(request, donor_id=1):
    donor = DonationRequests.objects.get(id=donor_id).donor
    send_mail("foodatdalteam@gmail.com", donor.email, "Organ Donation",
              """You've been requested by {} to donate organ. Thanks!""".format(request.user.hospital_name),
              server="smtp.gmail.com", username="foodatdalteam@gmail.com", password="foodatdal")
    return HttpResponse("Success")


def get_user_details(request):
    if request.POST:
        pass
    else:
        user_details = []
        temp_dict = {}
        hospital = User.objects.get(id=request.user.id)
        temp_dict["hospital_name"] = hospital.hospital_name
        temp_dict["hospital_email"] = hospital.email
        temp_dict["hospital_city"] = hospital.city
        temp_dict["hospital_province"] = hospital.province
        temp_dict["hospital_contact"] = hospital.contact_number
        user_details.append(temp_dict)
        user_json = json.dumps(user_details)
    return HttpResponse(user_json)


@csrf_exempt
def update_user_details(request):
    if request.POST:
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        city = request.POST.get('city', '')
        contact = request.POST.get('contact', '')
        province = request.POST.get('province', '')
        user = User.objects.get(id=request.user.id)
        user.email = request.POST.get('email', '')
        user.hospital_name = request.POST.get('name', '')
        user.city = request.POST.get('city', '')
        user.province = request.POST.get('province', '')
        user.contact_number = request.POST.get('contact', '')
        print("about to save...")
        user.save()
    return HttpResponse("success")


@csrf_exempt
def update_pwd_details(request):
    if request.POST:
        user = authenticate(username=request.user.username, password=request.POST.get("old_password", ""))
        if user is not None:
            user.set_password(request.POST.get("new_password", ""))
            print("about to save password...")
            user.save(update_fields=["password"])
    return HttpResponse("success")

def hospital_logout(request):
    logout(request)
    return redirect("hospital-login")

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from donors.models import Appointments
from donors.models import DonationRequests
   # Update if your models differ
import json

def fetch_donations(request):
    """Fetch pending donations for approved appointments"""
    donation_status = "Pending"
    appointment_status = "Approved"

    appointments = Appointments.objects.filter(
        Q(hospital__id=request.user.id) & 
        Q(appointment_status=appointment_status) & 
        Q(donation_request__donation_status=donation_status)
    ).select_related('donation_request', 'donation_request__donor')

    donation_list = []
    for appointment in appointments:
        donation_list.append({
            "first_name": appointment.donation_request.donor.first_name,
            "last_name": appointment.donation_request.donor.last_name,
            "organ": appointment.donation_request.organ_type,
            "donation_id": appointment.donation_request.id,
            "blood_group": appointment.donation_request.blood_type,
        })

    return JsonResponse({"data": donation_list})

def fetch_donation_details(request):
    donation_id = request.GET.get('donation_id', '')
    donations = DonationRequests.objects.filter(id=int(donation_id))
    donation_list = []
    for donation in donations:
        temp = {
            "first_name": donation.donor.first_name,
            "last_name": donation.donor.last_name,
            "email": donation.donor.email,
            "contact_number": donation.donor.contact_number,
            "city": donation.donor.city,
            "province": donation.donor.province,
            "country": donation.donor.country,
            "organ": donation.organ_type,
            "donation_id": donation.id,
            "blood_group": donation.blood_type,
            "donation_status": donation.donation_status,
            "family_member_name": donation.family_relation_name,
            "family_member_relation": donation.family_relation,
            "family_member_contact": donation.family_contact_number
        }
        donation_list.append(temp)
    return HttpResponse(json.dumps(donation_list))

@csrf_exempt
def approve_donation(request, donation_id):
    donation = get_object_or_404(DonationRequests, id=donation_id)
    donation.donation_status = "Approved"
    donation.save(update_fields=["donation_status"])
    return JsonResponse({"status": "approved"})

@csrf_exempt
def deny_donation(request, donation_id):
    donation = get_object_or_404(DonationRequests, id=donation_id)
    donation.donation_status = "Denied"
    donation.save(update_fields=["donation_status"])
    return JsonResponse({"status": "denied"})
