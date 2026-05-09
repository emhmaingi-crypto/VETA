from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentUser


@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_photo', 'institution', 'county', 'course', 'level', 'graduation_year', 'skills', 'linkedin_url', 'github_url', 'portfolio_url', 'cv', 'is_available')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'user_type', 'institution', 'course', 'level', 'is_available', 'is_staff')
    search_fields = ('username', 'email', 'institution', 'skills')
