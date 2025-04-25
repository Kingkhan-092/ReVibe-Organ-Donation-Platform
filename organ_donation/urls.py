"""organ_donation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path, path
from donors import views as v
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path('^donors/', include('donors.urls')),
    re_path('^hospitals/', include('hospitals.urls')),
    re_path('admin/', admin.site.urls),
    re_path('home/$', v.wedonate, name='wedonate'),
    re_path('about-us/', v.about_us, name='about-us'), 
    re_path('community/', v.community, name='community'),
    path('api/pending-appointments/', v.get_pending_appointments, name='get_pending_appointments'),
    re_path('', v.wedonate, name='home'),  # <-- This line handles http://127.0.0.1:8000/
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
