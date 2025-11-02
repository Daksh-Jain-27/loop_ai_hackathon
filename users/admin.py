# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, DoctorProfile 
from .models import Prescription, MedicalReport

class CustomUserAdmin(UserAdmin):
    # Add our custom 'role' field to the admin display
    list_display = ('email', 'username', 'role', 'is_staff')
    
    # Add 'role' to the fields you can edit
    # This groups fields into sections
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'role')}), # Add role here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # This is needed if you add 'role' to 'fieldsets'
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

    pass

# Register your custom User model with the custom admin class
admin.site.register(User, CustomUserAdmin)

admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(Prescription)   
admin.site.register(MedicalReport)