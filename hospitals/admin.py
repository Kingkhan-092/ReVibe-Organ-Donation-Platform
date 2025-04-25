# hospitals/admin.py
from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'hospital_name', 'province', 'contact_number', 'city', 'country')
    search_fields = ['hospital_name', 'username', 'city', 'province']
    ordering = ['hospital_name']

admin.site.register(User, UserAdmin)
