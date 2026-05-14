from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentUser


@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):
    # Used when ADDING a new user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name', 'email', 'user_type',
            'bio', 'profile_photo', 'phone_number', 'nationality',
            'institution', 'county', 'course', 'level', 'graduation_year',
            'id_number', 'languages', 'skills', 'certifications',
            'work_experience', 'achievements', 'projects', 'hobbies',
            'preferred_job_type', 'expected_salary', 'references',
            'linkedin_url', 'github_url', 'portfolio_url', 'cv', 'is_available',
        )}),
        ('Trainer fields', {'fields': (
            'trainer_title', 'trainer_department',
            'trainer_expertise', 'trainer_years_experience',
        )}),
        ('Company / Individual fields', {'fields': (
            'company_name', 'company_website', 'company_description',
        )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'user_type', 'institution', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'institution', 'skills')
    ordering = ('-date_joined',)
